import logging

def migrate(env):
    cr = env.cr
    # 1. Fetch old data
    cr.execute("SELECT * FROM contribuyentes")
    records = cr.dictfetchall()
    
    Partner = env['res.partner']
    count = 0
    errors = 0
    
    print(f"Iniciando migración de {len(records)} registros...")
    
    for r in records:
        try:
            with env.cr.savepoint():
                # Clean up padding spaces from CHAR fields
                tipo = r.get('con_tipo')
                tipo = tipo.strip() if tipo else 'PER'
                if tipo not in ['PER', 'EMP']:
                    tipo = 'PER'
                
                # Map doc_exp
                doc_exp = r.get('doc_exp')
                if doc_exp:
                    doc_exp = doc_exp.strip()
                    if doc_exp not in ['LP', 'CB', 'SC', 'OR', 'PT', 'TJ', 'CH', 'BE', 'PD']:
                        doc_exp = False
                
                vals = {
                    'is_contribuyente': True,
                    'con_pmc': r.get('con_pmc'),
                    'pmc_ant': str(r.get('pmc_ant')).strip() if r.get('pmc_ant') else False,
                    'con_tipo': tipo,
                    'con_nit': str(r.get('con_nit')).strip() if r.get('con_nit') else False,
                    'doc_tipo': r.get('doc_tipo').strip() if r.get('doc_tipo') else False,
                    'doc_num': r.get('doc_num').strip() if r.get('doc_num') else False,
                    'doc_exp': doc_exp,
                    'con_fech_ini': r.get('con_fech_ini'),
                    'con_fecnac': r.get('con_fecnac'),
                    'phone': r.get('con_tel').strip() if r.get('con_tel') else False,
                    'comment': r.get('con_obs'),
                }
                
                if tipo == 'PER':
                    vals.update({
                        'con_pat': r.get('con_pat').strip() if r.get('con_pat') else 'S/A', # Fallback for constraints
                        'con_mat': r.get('con_mat').strip() if r.get('con_mat') else False,
                        'con_nom1': r.get('con_nom1').strip() if r.get('con_nom1') else False,
                        'con_nom2': r.get('con_nom2').strip() if r.get('con_nom2') else False,
                    })
                    names = [vals['con_pat'], vals['con_mat'], vals['con_nom1'], vals['con_nom2']]
                    vals['name'] = " ".join([n for n in names if n])
                else:
                    vals.update({
                        'con_raz': r.get('con_raz').strip() if r.get('con_raz') else 'Sin Razón Social',
                        'con_pat': r.get('con_pat').strip() if r.get('con_pat') else 'Representante',
                    })
                    vals['name'] = vals['con_raz']
                    
                # dom
                vals.update({
                    'dom_ciu': r.get('dom_ciu').strip() if r.get('dom_ciu') else False,
                    'dom_bar': r.get('dom_bar').strip() if r.get('dom_bar') else False,
                    'dom_nom': r.get('dom_nom').strip() if r.get('dom_nom') else False,
                    'dom_num': r.get('dom_num').strip() if r.get('dom_num') else False,
                })
                
                # Fix doc_num uniqueness
                if vals['doc_num']:
                    if Partner.search_count([('doc_num', '=', vals['doc_num']), ('is_contribuyente', '=', True)]):
                        vals['doc_num'] = vals['doc_num'] + f"-DUP-{r.get('id_contrib', count)}"
                
                # Check required fields logic to avoid fails
                if vals['dom_bar'] and not vals['dom_ciu']:
                    vals['dom_ciu'] = 'Ciudad Desconocida'
                if vals['dom_num'] and not vals['dom_nom']:
                    vals['dom_nom'] = 'S/N'
                
                Partner.sudo().create(vals)
                count += 1
                
                if count % 100 == 0:
                    print(f"Procesados {count} registros...")
                    
        except Exception as e:
            errors += 1
            print(f"Error importando registro PMC {r.get('con_pmc')}: {str(e)}")
            
    print(f"Migración completada: {count} exitosos, {errors} con errores.")
    env.cr.commit()

migrate(env)
