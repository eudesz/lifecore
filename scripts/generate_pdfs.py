import random
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from faker import Faker
import os

fake = Faker('es_ES')

LAB_TEMPLATES = [
    {
        'title': 'Perfil Lipídico y Glucosa',
        'tests': [
            ('Glucosa en Ayunas', 'mg/dL', 70, 100),
            ('Colesterol Total', 'mg/dL', 125, 200),
            ('Colesterol HDL', 'mg/dL', 40, 60),
            ('Colesterol LDL', 'mg/dL', 0, 100),
            ('Triglicéridos', 'mg/dL', 0, 150),
        ]
    },
    {
        'title': 'Hemograma Completo',
        'tests': [
            ('Hemoglobina', 'g/dL', 13.5, 17.5),
            ('Hematocrito', '%', 41, 50),
            ('Leucocitos', 'miles/uL', 4.5, 11.0),
            ('Plaquetas', 'miles/uL', 150, 450),
        ]
    }
]

CLINICS = [
    "Laboratorio Central Clinica Santa Maria",
    "Diagnósticos Precisos S.A.",
    "Centro Médico Metropolitano - Laboratorio",
    "BioAnalysis Corp"
]

def generate_lab_pdf(filename, date_str, patient_name="Alexander Doe", patient_age=45):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    clinic = random.choice(CLINICS)
    elements.append(Paragraph(f"<b>{clinic}</b>", styles['Heading1']))
    elements.append(Paragraph(f"Fecha: {date_str}", styles['Normal']))
    elements.append(Paragraph(f"Paciente: {patient_name}", styles['Normal']))
    elements.append(Paragraph(f"Edad: {patient_age} años", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Select template
    template = random.choice(LAB_TEMPLATES)
    elements.append(Paragraph(f"<b>{template['title']}</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Table Data
    data = [['Análisis', 'Resultado', 'Unidades', 'Rango Ref.']]
    
    # Simulate health condition based on age roughly (simplified logic here)
    is_unhealthy = patient_age > 40
    
    for test_name, unit, min_ref, max_ref in template['tests']:
        if is_unhealthy and test_name == 'Glucosa en Ayunas':
            val = random.randint(110, 160) # High glucose
        elif is_unhealthy and test_name == 'Colesterol LDL':
            val = random.randint(130, 180) # High cholesterol
        else:
            val = random.randint(int(min_ref), int(max_ref) + 10)
            
        # Flag abnormal
        flag = ""
        if val < min_ref or val > max_ref:
            flag = " *"
            
        data.append([
            f"{test_name}", 
            f"{val}{flag}", 
            unit, 
            f"{min_ref} - {max_ref}"
        ])

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Validado por: {fake.name()} - Bioquímico M.P. {random.randint(1000,9999)}", styles['Italic']))
    
    doc.build(elements)

def main():
    # Generate 1 report per year from 2005 to 2025
    out_dir = 'sample_data/full_history/documents'
    os.makedirs(out_dir, exist_ok=True)
    
    birth_year = 1975
    
    for year in range(2005, 2026):
        date = datetime(year, random.randint(1, 12), random.randint(1, 28))
        age = year - birth_year
        fname = os.path.join(out_dir, f"lab_report_{year}.pdf")
        generate_lab_pdf(fname, date.strftime("%Y-%m-%d"), patient_age=age)
        print(f"Generated {fname}")

if __name__ == "__main__":
    main()

