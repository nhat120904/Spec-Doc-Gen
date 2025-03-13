import pypandoc

# First convert MD to LaTeX
latex_output = pypandoc.convert_file('./generated_docs/bookstoreweb/software_specification.md', 'latex')

# Then convert LaTeX to DOCX
pypandoc.convert_text(latex_output, 'docx', format='latex', outputfile='output.docx')