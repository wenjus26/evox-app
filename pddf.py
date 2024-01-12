from weasyprint import HTML, CSS
html_string = """
<html>
    <head>
    <title>exemple</title>
    <style>
    @page {
        size:A5;
        margin:0
    }
    body {
        font-family: Arial, sans-serif;padding:20px
    }
    </style>
    </head>
    <body>
    good good 
    </body>
    
</html>
"""
HTML(string=html_string).write_pdf('ro.pdf',styleshetts=[CSS(string='@page {size:A5; margin:0;}')])
 
    
print("fichier pdf au format a5 generer ")