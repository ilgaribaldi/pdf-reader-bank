from utils.bbva_bank import get_bbva_bank_statement_test
import pprint as pp

path = "../test_pdfs/pdf1.pdf"

response = get_bbva_bank_statement_test(path)

pp.pprint(response)