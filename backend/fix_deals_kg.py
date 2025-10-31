import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.parser import parser
from app.services.kg_builder import kg_builder

user_id = "112944693963105753678"
file_id = "b2ed46f9635e41ffbb02582c90db545c21215c8177316c97a6b88eab0e57c4a4"
file_path = f"uploads/{user_id}_{file_id}.docx"

print(f"Processing Deals file...")
parsed_data = parser.parse_file(file_path)
print(f"Parsed {len(parsed_data)} items")

kg_result = kg_builder.build_graph(parsed_data, file_id, user_id, doc_type="deals")
print(f"Result: {kg_result}")
