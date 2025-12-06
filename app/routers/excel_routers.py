from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
from typing import Optional
import io
import xlsxwriter
from datetime import datetime, timedelta
from models.models import User,Citizen,Certificates,Privilege
from db.db import get_session
from routers.auth import get_current_user
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI


router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Получение статистики по льготникам"""
    
    # Общее количество льготников
    total_citizens_query = select(func.count(Citizen.id))
    total_citizens = db.exec(total_citizens_query).first() or 0
    
    # Общее количество льгот
    total_privileges_query = select(func.count(Privilege.id))
    total_privileges = db.exec(total_privileges_query).first() or 0
    
    # Распределение по льготам
    privilege_distribution_query = (
        select(
            Privilege.id,
            Privilege.code,
            Privilege.name,
            Privilege.description,
            func.count(Citizen.id).label('citizen_count')
        )
        .join(Citizen, Privilege.id == Citizen.privilege_id, isouter=True)
        .group_by(Privilege.id)
        .order_by(func.count(Citizen.id).desc())
    )
    
    privilege_results = db.exec(privilege_distribution_query).all()
    privilege_distribution = [
        {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "description": row.description,
            "citizen_count": row.citizen_count
        }
        for row in privilege_results
    ]
    
    # Всего справок
    certificates_query = select(func.count(Certificates.id))
    certificates_issued = db.exec(certificates_query).first() or 0
    
    # Справки за последний месяц
    month_ago = datetime.now() - timedelta(days=30)
    last_month_query = (
        select(func.count(Certificates.id))
        .where(Certificates.issue_date >= month_ago.date())
    )
    last_month_certificates = db.exec(last_month_query).first() or 0
    
    return {
        "total_citizens": total_citizens,
        "total_privileges": total_privileges,
        "privilege_distribution": privilege_distribution,
        "certificates_issued": certificates_issued,
        "last_month_certificates": last_month_certificates
    }


@router.get("/privileges/excel")
async def export_privileges_excel(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Экспорт отчета по льготным категориям в Excel"""
    
    # Получаем данные
    query = (
        select(
            Privilege.code,
            Privilege.name,
            Privilege.description,
            func.count(Citizen.id).label('count')
        )
        .join(Citizen, Privilege.id == Citizen.privilege_id, isouter=True)
        .group_by(Privilege.id, Privilege.code, Privilege.name, Privilege.description)
        .order_by(Privilege.code)
    )
    
    results = db.exec(query).all()
    
    # Создаем Excel файл в памяти
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Льготные категории')
    
    # Форматы
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'valign': 'vcenter'
    })
    
    # Заголовки
    headers = ['Код льготы', 'Наименование', 'Описание', 'Количество льготников']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
        worksheet.set_column(col, col, 25)  # Ширина колонок
    
    # Данные
    for row_idx, row in enumerate(results, start=1):
        worksheet.write(row_idx, 0, row.code, cell_format)
        worksheet.write(row_idx, 1, row.name, cell_format)
        worksheet.write(row_idx, 2, row.description or '', cell_format)
        worksheet.write(row_idx, 3, row.count, cell_format)
    worksheet.autofilter(0, 0, len(results), len(headers) - 1)
    
    # Закрываем книгу
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=privileges_report.xlsx"}
    )


@router.get("/citizens/excel")
async def export_citizens_excel(
    privilege_id: Optional[int] = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Экспорт списка льготников в Excel"""
    
    # Формируем запрос
    query = (
        select(
            Citizen.lastname,
            Citizen.firstname,
            Citizen.middlename,
            Citizen.id_snils,
            Privilege.code.label('privilege_code'),
            Privilege.name.label('privilege_name')
        )
        .join(Privilege, Citizen.privilege_id == Privilege.id, isouter=True)
    )
    
    if privilege_id:
        query = query.where(Citizen.privilege_id == privilege_id)
    
    query = query.order_by(Citizen.lastname, Citizen.firstname)
    
    results = db.exec(query).all()
    
    # Создаем Excel файл
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Льготники')
    
    # Форматы
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'valign': 'vcenter'
    })
    
    # Заголовки
    headers = ['Фамилия', 'Имя', 'Отчество', 'СНИЛС', 'Код льготы', 'Наименование льготы']
    col_widths = [20, 15, 20, 15, 15, 25]
    
    for col, (header, width) in enumerate(zip(headers, col_widths)):
        worksheet.write(0, col, header, header_format)
        worksheet.set_column(col, col, width)
    
    # Данные
    for row_idx, row in enumerate(results, start=1):
        worksheet.write(row_idx, 0, row.lastname, cell_format)
        worksheet.write(row_idx, 1, row.firstname, cell_format)
        worksheet.write(row_idx, 2, row.middlename or '', cell_format)
        worksheet.write(row_idx, 3, row.id_snils or '', cell_format)
        worksheet.write(row_idx, 4, row.privilege_code or '', cell_format)
        worksheet.write(row_idx, 5, row.privilege_name or '', cell_format)
    
    # Автофильтр
    worksheet.autofilter(0, 0, len(results), len(headers) - 1)
    
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=citizens_report.xlsx"}
    )


@router.get("/charts/distribution")
async def get_distribution_chart(
    chart_type: str = Query("bar", regex="^(bar|pie|line)$"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Генерация диаграммы распределения льготников по категориям"""
    
    # Получаем данные
    query = (
        select(
            Privilege.name,
            func.count(Citizen.id).label('count')
        )
        .join(Citizen, Privilege.id == Citizen.privilege_id, isouter=True)
        .group_by(Privilege.id, Privilege.name)
        .order_by(func.count(Citizen.id).desc())
    )
    
    results = db.exec(query).all()
    
    # Подготавливаем данные для диаграммы
    categories = [row.name for row in results]
    counts = [row.count for row in results]
    
    # Создаем диаграмму
    plt.figure(figsize=(12, 6))
    
    if chart_type == "bar":
        plt.bar(categories, counts)
        plt.title('Распределение льготников по категориям льгот')
        plt.xlabel('Категории льгот')
        plt.ylabel('Количество льготников')
        plt.xticks(rotation=45, ha='right')
        
    elif chart_type == "pie":
        plt.pie(counts, labels=categories, autopct='%1.1f%%')
        plt.title('Распределение льготников по категориям льгот')
        
    elif chart_type == "line":
        plt.plot(categories, counts, marker='o')
        plt.title('Распределение льготников по категориям льгот')
        plt.xlabel('Категории льгот')
        plt.ylabel('Количество льготников')
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Сохраняем диаграмму в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    plt.close()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=distribution_chart.png"}
    )


@router.get("/charts/certificates-timeline")
async def get_certificates_timeline_chart(
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """График выдачи справок по времени"""
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    query = (
        select(
            Certificates.issue_date,
            func.count(Certificates.id).label('count')
        )
        .where(Certificates.issue_date >= start_date)
        .group_by(Certificates.issue_date)
        .order_by(Certificates.issue_date)
    )
    
    results = db.exec(query).all()
    
    # Подготавливаем данные
    dates = [row.issue_date for row in results]
    counts = [row.count for row in results]
    
    # Создаем график
    plt.figure(figsize=(14, 6))
    
    if len(dates) > 1:
        plt.plot(dates, counts, marker='o', linestyle='-', linewidth=2)
    else:
        plt.bar([str(d) for d in dates], counts)
    
    plt.title(f'Выдача справок за последние {days} дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество справок')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    plt.close()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=certificates_timeline.png"}
    )


@router.get("/excel/full-report")
async def export_full_report(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Полный отчет в Excel с несколькими листами"""
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Общие форматы
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'valign': 'vcenter'
    })
    
    
    # 1. Лист со статистикой
    stats = await get_statistics(db, current_user)
    ws_stats = workbook.add_worksheet('Статистика')
    
    ws_stats.write(0, 0, 'Показатель', header_format)
    ws_stats.write(0, 1, 'Значение', header_format)
    ws_stats.set_column(0, 0, 35)
    ws_stats.set_column(1, 1, 20)
    
    stats_data = [
        ("Общее количество льготников", stats["total_citizens"]),
        ("Количество категорий льгот", stats["total_privileges"]),
        ("Всего выдано справок", stats["certificates_issued"]),
        ("Справок за последний месяц", stats["last_month_certificates"])
    ]
    
    for row_idx, (label, value) in enumerate(stats_data, start=1):
        ws_stats.write(row_idx, 0, label, cell_format)
        ws_stats.write(row_idx, 1, value, cell_format)
    
    # 2. Лист с распределением по льготам
    ws_dist = workbook.add_worksheet('Распределение по льготам')
    
    dist_headers = ['Категория', 'Код', 'Количество', 'Описание']
    for col, header in enumerate(dist_headers):
        ws_dist.write(0, col, header, header_format)
    
    ws_dist.set_column(0, 0, 30)  # Категория
    ws_dist.set_column(1, 1, 15)  # Код
    ws_dist.set_column(2, 2, 15)  # Количество
    ws_dist.set_column(3, 3, 40)  # Описание
    
    for row_idx, item in enumerate(stats["privilege_distribution"], start=1):
        ws_dist.write(row_idx, 0, item["name"], cell_format)
        ws_dist.write(row_idx, 1, item["code"], cell_format)
        ws_dist.write(row_idx, 2, item["citizen_count"], cell_format)
        ws_dist.write(row_idx, 3, item["description"] or "", cell_format)
    
    ws_dist.autofilter(0, 0, len(stats["privilege_distribution"]), len(dist_headers) - 1)
    
    # 3. Лист со всеми льготниками
    ws_citizens = workbook.add_worksheet('Все льготники')
    citizens_headers = ['Фамилия', 'Имя', 'Отчество', 'СНИЛС', 'Дата регистрации', 'Код льготы', 'Льгота']
    citizens_widths = [20, 15, 20, 15, 20, 15, 25]
    
    for col, (header, width) in enumerate(zip(citizens_headers, citizens_widths)):
        ws_citizens.write(0, col, header, header_format)
        ws_citizens.set_column(col, col, width)
    
    citizens_query = (
        select(
            Citizen.lastname,
            Citizen.firstname,
            Citizen.middlename,
            Citizen.id_snils,
            Citizen.created_at,
            Privilege.code,
            Privilege.name
        )
        .join(Privilege, Citizen.privilege_id == Privilege.id, isouter=True)
        .order_by(Citizen.lastname, Citizen.firstname)
    )
    
    citizens_results = db.exec(citizens_query).all()
    
    for row_idx, row in enumerate(citizens_results, start=1):
        ws_citizens.write(row_idx, 0, row.lastname, cell_format)
        ws_citizens.write(row_idx, 1, row.firstname, cell_format)
        ws_citizens.write(row_idx, 2, row.middlename or "", cell_format)
        ws_citizens.write(row_idx, 3, row.id_snils or "", cell_format)
        ws_citizens.write(row_idx, 4, row.created_at.date().isoformat() if row.created_at else "", cell_format)
        ws_citizens.write(row_idx, 5, row.code or "", cell_format)
        ws_citizens.write(row_idx, 6, row.name or "", cell_format)
    
    ws_citizens.autofilter(0, 0, len(citizens_results), len(citizens_headers) - 1)
    
    # 4. Лист со справками
    ws_certificates = workbook.add_worksheet('Выданные справки')
    
    cert_headers = ['Номер справки', 'Дата выдачи', 'Кем выдана', 'Цель', 'Льготник']
    cert_widths = [20, 15, 25, 30, 30]
    
    for col, (header, width) in enumerate(zip(cert_headers, cert_widths)):
        ws_certificates.write(0, col, header, header_format)
        ws_certificates.set_column(col, col, width)
    
    certificates_query = (
        select(
            Certificates.number_certificate,
            Certificates.issue_date,
            Certificates.issued_by,
            Certificates.purpose,
            Citizen.lastname,
            Citizen.firstname,
            Citizen.middlename
        )
        .join(Citizen, Certificates.citizen_id == Citizen.id)
        .order_by(Certificates.issue_date.desc())
    )
    
    cert_results = db.exec(certificates_query).all()
    
    for row_idx, row in enumerate(cert_results, start=1):
        ws_certificates.write(row_idx, 0, row.number_certificate or "", cell_format)
        ws_certificates.write(row_idx, 1, row.issue_date.isoformat() if row.issue_date else "", cell_format)
        ws_certificates.write(row_idx, 2, row.issued_by or "", cell_format)
        ws_certificates.write(row_idx, 3, row.purpose or "", cell_format)
        full_name = f"{row.lastname} {row.firstname}"
        if row.middlename:
            full_name += f" {row.middlename}"
        ws_certificates.write(row_idx, 4, full_name.strip(), cell_format)
    
    ws_certificates.autofilter(0, 0, len(cert_results), len(cert_headers) - 1)
    
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=full_report.xlsx"}
    )