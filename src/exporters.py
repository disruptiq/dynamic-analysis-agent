"""
Export functions for scan results.
"""

import json
import datetime
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

from .logger import logger


def export_results(results, output_format="json", output_file=None):
    """
    Export scan results to file.

    Args:
        results (dict): Scan results
        output_format (str): Output format (json, html, pdf, csv)
        output_file (str): Output file path
    """
    if not results:
        return

    if not output_file:
        timestamp = datetime.datetime.fromtimestamp(results["timestamp"]).strftime("%Y%m%d_%H%M%S")
        output_file = f"scan_results_{timestamp}.{output_format}"

    if output_format == "json":
        export_json(results, output_file)
    elif output_format == "html":
        export_html(results, output_file)
    elif output_format == "pdf":
        export_pdf(results, output_file)
    elif output_format == "csv":
        export_csv(results, output_file)
    else:
        print(f"Unsupported output format: {output_format}")


def export_json(results, output_file):
    """
    Export results to JSON file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")


def export_html(results, output_file):
    """
    Export results to HTML file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        html_content = generate_html_report(results)
        with open(output_file, 'w') as f:
            f.write(html_content)
        logger.info(f"HTML report exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting HTML: {e}")


def generate_html_report(results):
    """
    Generate HTML report from scan results.

    Args:
        results (dict): Scan results

    Returns:
        str: HTML content
    """
    timestamp = datetime.datetime.fromtimestamp(results["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dynamic Analysis Scan Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ background: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .vulnerabilities {{ margin: 20px 0; }}
            .vulnerability {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .high {{ border-left: 5px solid #dc3545; }}
            .medium {{ border-left: 5px solid #ffc107; }}
            .low {{ border-left: 5px solid #28a745; }}
            .tools {{ margin: 20px 0; }}
            .tool {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Dynamic Analysis Security Scan Report</h1>
            <p><strong>Target:</strong> {results['target']}</p>
            <p><strong>Scan Date:</strong> {timestamp}</p>
        </div>

        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Vulnerabilities:</strong> {results['summary']['total_vulnerabilities']}</p>
            <p><strong>Tools Run:</strong> {results['summary']['tools_run']}</p>
            <p><strong>Scan Duration:</strong> {results['summary']['scan_duration']:.2f} seconds</p>
            <p><strong>Connectivity:</strong> {'✓ OK' if results.get('connectivity') else '✗ Failed'}</p>
        </div>

        <div class="vulnerabilities">
            <h2>Vulnerabilities Found ({len(results['vulnerabilities'])})</h2>
    """

    for vuln in results['vulnerabilities']:
        severity_class = "low"
        if "SQL" in vuln['type'] or "Command" in vuln['type']:
            severity_class = "high"
        elif "XSS" in vuln['type']:
            severity_class = "medium"

        html += f"""
            <div class="vulnerability {severity_class}">
                <h3>{vuln['type']}</h3>
                <p><strong>Endpoint:</strong> {vuln['endpoint']}</p>
                <p><strong>Method:</strong> {vuln.get('method', 'N/A')}</p>
                <p><strong>Payload:</strong> {vuln.get('payload', 'N/A')}</p>
                <p><strong>Evidence:</strong> {vuln.get('evidence', 'N/A')}</p>
            </div>
        """

    html += """
        </div>

        <div class="tools">
            <h2>Tool Results</h2>
    """

    for tool in results['tools']:
        html += f"""
            <div class="tool">
                <h3>{tool['name'].upper()}</h3>
                <p><strong>Success:</strong> {tool['results'].get('success', 'Unknown')}</p>
                <p><strong>Timestamp:</strong> {datetime.datetime.fromtimestamp(tool['results'].get('timestamp', 0)).strftime('%H:%M:%S')}</p>
                {"<pre>" + tool['results'].get('output', '') + "</pre>" if tool['results'].get('output') else ""}
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html


def export_pdf(results, output_file):
    """
    Export results to PDF file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
        )
        story.append(Paragraph("Dynamic Analysis Security Scan Report", title_style))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 6))

        summary_data = [
            ["Target", results['target']],
            ["Scan Date", datetime.datetime.fromtimestamp(results["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Vulnerabilities", str(results['summary']['total_vulnerabilities'])],
            ["Tools Run", str(results['summary']['tools_run'])],
            ["Scan Duration", f"{results['summary']['scan_duration']:.2f} seconds"],
            ["Connectivity", "OK" if results.get('connectivity') else "Failed"]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Vulnerability Breakdown
        if results['vulnerabilities']:
            story.append(Paragraph("Vulnerability Details", styles['Heading2']))
            story.append(Spacer(1, 6))

            vuln_data = [["Type", "Endpoint", "Method", "Evidence"]]
            for vuln in results['vulnerabilities'][:50]:  # Limit to 50 for PDF
                vuln_data.append([
                    vuln['type'][:30] + "..." if len(vuln['type']) > 30 else vuln['type'],
                    vuln['endpoint'][:50] + "..." if len(vuln['endpoint']) > 50 else vuln['endpoint'],
                    vuln.get('method', 'N/A'),
                    vuln.get('evidence', 'N/A')[:40] + "..." if len(vuln.get('evidence', '')) > 40 else vuln.get('evidence', '')
                ])

            vuln_table = Table(vuln_data, colWidths=[1.5*inch, 2.5*inch, 0.8*inch, 2*inch])
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(vuln_table)
            story.append(Spacer(1, 20))

        # Tool Results
        if results['tools']:
            story.append(Paragraph("Tool Results", styles['Heading2']))
            story.append(Spacer(1, 6))

            for tool in results['tools']:
                story.append(Paragraph(f"{tool['name'].upper()}", styles['Heading3']))
                story.append(Paragraph(f"Status: {tool['results'].get('success', 'Unknown')}", styles['Normal']))
                story.append(Paragraph(f"Duration: {datetime.datetime.fromtimestamp(tool['results'].get('timestamp', 0)).strftime('%H:%M:%S')}", styles['Normal']))

                if tool['results'].get('output'):
                    output_text = tool['results']['output'][:500] + "..." if len(tool['results']['output']) > 500 else tool['results']['output']
                    story.append(Paragraph(f"Output: {output_text}", styles['Normal']))

                story.append(Spacer(1, 12))

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by Dynamic Analysis Agent", styles['Italic']))

        doc.build(story)
        logger.info(f"PDF report exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")


def export_csv(results, output_file):
    """
    Export results to CSV file.

    Args:
        results (dict): Scan results
        output_file (str): Output file path
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['type', 'endpoint', 'method', 'payload', 'evidence', 'severity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for vuln in results['vulnerabilities']:
                # Determine severity based on vulnerability type
                vuln_type = vuln['type'].lower()
                if 'sql' in vuln_type or 'command' in vuln_type or 'xxe' in vuln_type or 'ssrf' in vuln_type:
                    severity = 'High'
                elif 'xss' in vuln_type or 'csrf' in vuln_type:
                    severity = 'Medium'
                else:
                    severity = 'Low'

                writer.writerow({
                    'type': vuln['type'],
                    'endpoint': vuln['endpoint'],
                    'method': vuln.get('method', ''),
                    'payload': vuln.get('payload', ''),
                    'evidence': vuln.get('evidence', ''),
                    'severity': severity
                })

        logger.info(f"CSV report exported to {output_file}")
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
