from sqlmodel import Session, select, or_, col
from models.models import EventLog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from typing import Optional, List
from models.models import User
import io
from fastapi.responses import StreamingResponse
import xlsxwriter
from db.db import get_session
from routers.auth import get_current_user

router = APIRouter(prefix='/api/v1/logs', tags=['logs'])

class EventlogData(BaseModel):
    user_id: Optional[int]
    action: str
    object_type: str
    object_id: Optional[str]
    created_at: datetime 
    model_config = {"from_attributes": True}

@router.get("/", response_model=List[EventlogData], description="")
def get_all_logs(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
   
):
    
    query = select(EventLog)
    logs = session.exec(query).all()
    return logs

@router.get("/filter/", response_model=List[EventlogData], description="")
def get_logs_by_user_and_date(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
    user_id: int = Query(..., description="Фильтр по юзеру"),
    start_date: date = Query(..., description="Дата с (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата по date (YYYY-MM-DD)"),
):
   
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    query = select(EventLog).where(
        EventLog.user_id == user_id,
        EventLog.created_at >= start_datetime,
        EventLog.created_at <= end_datetime
    ).order_by(EventLog.created_at.desc())
    
    logs = session.exec(query).all()
    if not logs:
        return []
    return logs




@router.get("/user/{user_id}/export/", description="Экспорт логов пользователя в Excel")
def export_user_logs_to_excel(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
    days: Optional[int] = Query(30, ge=1, le=365, description="Дней назад"),
):
    """Экспорт логов пользователя в Excel файл"""
    
    query = select(EventLog).where(EventLog.user_id == user_id)
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.where(EventLog.created_at >= cutoff_date)
    
    query = query.order_by(EventLog.created_at.desc())
    logs = session.exec(query).all()
    
    if not logs:
        raise HTTPException(
            status_code=404,
            detail="Логи для указанного пользователя не найдены"
        )
    output = io.BytesIO()
    
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Логи")
    
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd.mm.yyyy hh:mm:ss',
        'border': 1
    })
    
    cell_format = workbook.add_format({'border': 1})
    
    headers = [
        "ID", "ID пользователя", "Действие", "Тип объекта", 
        "ID объекта", "Дата создания",
    ]
    
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)
    
    for row_num, log in enumerate(logs, start=1):
        worksheet.write(row_num, 0, log.id, cell_format)
        worksheet.write(row_num, 1, log.user_id, cell_format)
        worksheet.write(row_num, 2, log.action, cell_format)
        worksheet.write(row_num, 3, log.object_type, cell_format)
        worksheet.write(row_num, 4, log.object_id, cell_format)
        worksheet.write(row_num, 5, log.created_at, date_format)
        
    
    for col_num in range(len(headers)):
        worksheet.set_column(col_num, col_num, 20)
    
    worksheet.autofilter(0, 0, len(logs), len(headers) - 1)
    
    if len(logs) > 0:
        worksheet_pivot = workbook.add_worksheet("Статистика")
        from collections import Counter
        actions_counter = Counter(log.action for log in logs)
        
        worksheet_pivot.write(0, 0, "Действие", header_format)
        worksheet_pivot.write(0, 1, "Количество", header_format)
        
        for row_num, (action, count) in enumerate(actions_counter.items(), start=1):
            worksheet_pivot.write(row_num, 0, action, cell_format)
            worksheet_pivot.write(row_num, 1, count, cell_format)
        
    
    workbook.close()
    output.seek(0)
    filename = f"user_{user_id}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

   