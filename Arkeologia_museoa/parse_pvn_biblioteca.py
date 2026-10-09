import json, re

fields = """AUTOR 
TITULO 
LOCAL_FISICA 
TIPO_PUBLIC 
MATERIAS 
CRONOLOGIAS 
IDIOMAS 
INDICE 
LUGAR_FECHA_EDIC 
FECHA_ENTRADA 
OBSERVACIONES 
PRESTAMO """.split('\n')

result= {}
with open('PVN_Biblioteca.txt', 'r', encoding="iso-8859-15") as f:
    content = f.read()
    entries = content.split('\nN-REGISTRO ')
    for entry in entries:

        for field in fields:
            entry = re.sub(rf"({field})", r"|\1", entry)
        print(entry)

        field_contents = entry.split('|')
        register_ids = field_contents.pop(0).strip()
        if register_ids == "":
            register_ids = "0"
        registro = {"raw": f"N-REGISTRO {entry}", "parsed": {"registro_ids": register_ids.split(" / ")}}
        for content in field_contents:
            for field in fields:
                if content.startswith(field):
                    if field == "LUGAR_FECHA_EDIC ":
                        lugar_fecha_re = re.search(fr'{field}([^,]+), *(\d+)', content)
                        if lugar_fecha_re:
                            registro['parsed']['lugar_edic'] = lugar_fecha_re.group(1)
                            registro['parsed']['fecha_edic'] = lugar_fecha_re.group(2)
                        else:
                            registro['parsed']['lugar_fecha_edic'] = re.sub(r'[ \n]*$', '', re.sub(rf"^{field}", "", content))
                    else:
                        registro['parsed'][field.lower().strip()] = re.sub(r'[ \n]*$', '', re.sub(rf"^{field}", "", content))
        while register_ids in result:
            print(f"double register: {register_ids}")
            register_ids = register_ids + "-bis"
        result.update({register_ids: registro})

with open('PVN_Biblioteca.json', 'w') as f:
    json.dump(result, f, indent=2)
