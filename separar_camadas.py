import geopandas as gpd
import os
from tqdm import tqdm
import glob
import re

# --- 1. CONFIGURAÇÃO ---

# Caminho para o shapefile de municípios
CAMINHO_MUNICIPIOS = 'dados_entrada/MG_Municipios_2024.shp'

# --- IMPORTANTE: AJUSTE AQUI ---
# Lembre-se de ajustar estes nomes com base no seu arquivo de municípios
COLUNA_NOME_MUNICIPIO = "nome"  # <-- MUDE AQUI (ex: "NM_MUNICIP" ou "NOME_MUN")
COLUNA_CODIGO_MUNICIPIO = "geocodigo" # <-- MUDE AQUI (ex: "CD_MUNICIP" ou "COD_IBGE")
# --- FIM DO AJUSTE ---

# Dicionário com TODAS as configurações de camadas possíveis
TODAS_AS_CAMADAS = {
    'APPS': {
        'caminho_padrao': 'dados_entrada/APPS_*.shp', 
        'geometrias': ['Polygon']  # ATUALIZADO para Polygon
    },
    'RESERVA_LEGAL': {
        'caminho_padrao': 'dados_entrada/RESERVA_LEGAL_*.shp', # ATUALIZADO o caminho
        'geometrias': ['Polygon']                             # ATUALIZADO para Polygon
    }
}

pasta_saida_principal = 'dados_saida_shp_processados' 

# --- FIM DA CONFIGURAÇÃO ---

def sanitizar_nome_pasta(nome):
    """Limpa o nome para usar como pasta"""
    nome_sem_acento = "".join(c for c in str(nome) if c.isalnum() or c.isspace())
    return nome_sem_acento.replace(' ', '_').lower()

def processar_arquivos(municipios_gdf, config, nome_camada):
    """
    Processa arquivos (usando glob), faz o sjoin, e salva em pastas separadas.
    (Esta função não precisa de alterações)
    """
    arquivos_entrada = sorted(glob.glob(config['caminho_padrao']))
    if not arquivos_entrada:
        print(f"\nAviso: Nenhum arquivo encontrado para a camada '{nome_camada}'.")
        print(f"Verifique o 'caminho_padrao': {config['caminho_padrao']}")
        return

    print(f"\n--- Processando {len(arquivos_entrada)} arquivo(s) para: {nome_camada} ---")

    for idx, arquivo in enumerate(tqdm(arquivos_entrada, desc=f"Progresso de {nome_camada}")):
        try:
            dados_gdf = gpd.read_file(arquivo)
        except Exception as e:
            print(f"\nErro ao ler {arquivo}. Pulando. Detalhes: {e}")
            continue

        if dados_gdf.crs != municipios_gdf.crs:
            dados_gdf = dados_gdf.to_crs(municipios_gdf.crs)

        dados_com_municipio = gpd.sjoin(dados_gdf, municipios_gdf, how="inner", predicate="intersects")

        for tipo_geom in config['geometrias']:
            dados_filtrados = dados_com_municipio[dados_com_municipio.geometry.geom_type == tipo_geom]
            
            if dados_filtrados.empty:
                # Aviso movido para não poluir o log em cada arquivo
                pass 

            grupos = dados_filtrados.groupby(COLUNA_NOME_MUNICIPIO)

            for nome_municipio, grupo_gdf in grupos:
                try:
                    colunas_originais = [col for col in grupo_gdf.columns if col not in ['index_right', COLUNA_NOME_MUNICIPIO, COLUNA_CODIGO_MUNICIPIO]]
                    grupo_final = grupo_gdf[colunas_originais]
                    
                    nome_pasta = sanitizar_nome_pasta(nome_municipio)
                    caminho_pasta = os.path.join(pasta_saida_principal, nome_pasta)
                    os.makedirs(caminho_pasta, exist_ok=True)
                    
                    nome_saida = f"{nome_camada.lower()}_{tipo_geom.lower()}.shp"
                    caminho_saida = os.path.join(caminho_pasta, nome_saida)
                    
                    if idx == 0:
                        grupo_final.to_file(caminho_saida, driver='ESRI Shapefile', encoding='utf-8')
                    else:
                        grupo_final.to_file(caminho_saida, driver='ESRI Shapefile', mode='a', encoding='utf-8')

                except Exception as e:
                    print(f"\nErro ao salvar dados para {nome_municipio} ({tipo_geom}): {e}")

def main():
    """
    Função principal ATUALIZADA com o menu de seleção.
    """
    try:
        print("Carregando shapefile de municípios...")
        colunas_para_ler = [COLUNA_NOME_MUNICIPIO, COLUNA_CODIGO_MUNICIPIO, 'geometry']
        municipios_gdf = gpd.read_file(CAMINHO_MUNICIPIOS)[colunas_para_ler]
    except KeyError:
        print("\n--- ERRO CRÍTICO ---")
        print(f"Não encontrei as colunas '{COLUNA_NOME_MUNICIPIO}' ou '{COLUNA_CODIGO_MUNICIPIO}' no arquivo de municípios.")
        print("Por favor, abra o 'separar_camadas.py' e ajuste as variáveis 'COLUNA_NOME_MUNICIPIO' e 'COLUNA_CODIGO_MUNICIPIO' no topo do script.")
        return
    except Exception as e:
        print(f"ERRO CRÍTICO ao ler o arquivo de municípios: {e}")
        return

    # --- MENU DE SELEÇÃO ---
    print("\n" + "="*40)
    print("  O QUE VOCÊ DESEJA PROCESSAR?")
    print("[0] - APPs (Polígonos)")
    print("[1] - Reserva Legal (Polígonos)")
    print("="*40)
    choice = input("Digite 0 ou 1: ").strip()

    nome_camada_selecionada = None
    if choice == '0':
        nome_camada_selecionada = 'APPS'
    elif choice == '1':
        nome_camada_selecionada = 'RESERVA_LEGAL'
    else:
        print(f"\nERRO: Opção '{choice}' inválida. Saindo.")
        return # Sai do script se a opção for inválida

    # Pega a configuração correta do dicionário
    config_selecionada = TODAS_AS_CAMADAS.get(nome_camada_selecionada)

    # Chama o processamento apenas para a camada escolhida
    if config_selecionada:
        processar_arquivos(municipios_gdf, config_selecionada, nome_camada_selecionada)
        
        print(f"\n--- PROCESSO FINALIZADO ---")
        print(f"Dados salvos em: {pasta_saida_principal}")
    else:
        # Isso não deve acontecer se a lógica estiver correta
        print("ERRO: Configuração não encontrada.")


if __name__ == '__main__':
    main()
