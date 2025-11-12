A estrutura de arquivos deve seguir a seguinte organização:

Projeto_Hidrografia_APP/separar_camadas.py

Projeto_Hidrografia_APP/dados_entrada/

Projeto_Hidrografia_APP/dados_saida/

dentro da pasta dados_entrada, descompacte os arquivos da base de dados https://consultapublica.car.gov.br/publico/estados/downloads e os limites municipais https://idesisema.meioambiente.mg.gov.br/geonetwork/srv/por/catalog.search#/search?facet.q=topicCat%2FLimites
renomei os limites municiapis para "MG_Municipios_2024" .cst, .dbf, .prj, .shp e .shx

agora é só executar o separar_camadas.py e escolher a separar APPs ou RL
