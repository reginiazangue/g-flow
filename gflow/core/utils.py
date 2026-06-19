import csv
import io
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def projects_to_csv(projects):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID','Titre','Domaine','Technologies','Difficulté','Statut','Encadrant','Étudiants','Deadline','Créé le'])
    for p in projects:
        writer.writerow([
            p.id, p.title, p.domain, p.technologies, p.get_difficulty_display(),
            p.get_status_display(), p.teacher.get_full_name() or p.teacher.username,
            ', '.join(s.get_full_name() or s.username for s in p.students.all()),
            p.deadline.isoformat() if p.deadline else '',
            p.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return output.getvalue()


def project_to_pdf(project):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('GFTitle', parent=styles['Heading1'], textColor=colors.HexColor('#4F46E5'), fontSize=22, spaceAfter=12)
    h2 = ParagraphStyle('GFH2', parent=styles['Heading2'], textColor=colors.HexColor('#1E293B'), fontSize=14, spaceAfter=8)
    body = styles['BodyText']
    story = []
    story.append(Paragraph("G-Flow — Fiche Projet", title_style))
    story.append(Paragraph(project.title, h2))
    story.append(Spacer(1, 0.3*cm))
    data = [
        ['Domaine', project.domain],
        ['Technologies', project.technologies],
        ['Difficulté', project.get_difficulty_display()],
        ['Statut', project.get_status_display()],
        ['Encadrant', project.teacher.get_full_name() or project.teacher.username],
        ['Étudiants', ', '.join(s.get_full_name() or s.username for s in project.students.all()) or '—'],
        ['Deadline', project.deadline.strftime('%d/%m/%Y') if project.deadline else '—'],
        ['Créé le', project.created_at.strftime('%d/%m/%Y %H:%M')],
    ]
    table = Table(data, colWidths=[5*cm, 11*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EEF2FF')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#4F46E5')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Description", h2))
    story.append(Paragraph(project.description.replace('\n','<br/>'), body))
    doc.build(story)
    buf.seek(0)
    return buf.read()


def search_scholar(query, limit=8):
    try:
        r = requests.get('https://api.crossref.org/works',
                         params={'query': query, 'rows': limit, 'select': 'title,author,DOI,issued,URL'},
                         timeout=8)
        if r.status_code != 200:
            return []
        items = r.json().get('message', {}).get('items', [])
        results = []
        for it in items:
            results.append({
                'title': (it.get('title') or ['Sans titre'])[0],
                'authors': ', '.join(f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get('author', [])[:3]),
                'year': it.get('issued', {}).get('date-parts', [[None]])[0][0],
                'doi': it.get('DOI',''),
                'url': it.get('URL',''),
            })
        return results
    except Exception:
        return []


def notify(user, title, body='', url=''):
    from .models import Notification
    return Notification.objects.create(user=user, title=title, body=body, url=url)
