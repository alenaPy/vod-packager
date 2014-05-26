#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Force Schedule: Especifica el tipo de planificacione. (QImport.py)
#
# FORCE_SCHEDULE=True  -> Encola en Carbon Coder
# FORCE_SCHEDULE=False -> Encola en Rhozet solo lo que puede transcodificar
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
FORCE_SCHEDULE=False



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Sleep Time: Tiempo en que los Daemons duermen esperando nuevos trabajos
#
# GLOBAL_SLEEP_TIME=True  -> Todos los Daemons duermen SLEEP_TIME
# GLOBAL_SLEEP_TIME=False -> Cada Daemon Duerme el Tiempo Espeficado
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
GLOBAL_SLEEP_TIME=True
SLEEP_TIME=300
QIMPORT_SLEEP=300
QPULL_SLEEP=100
QCHECKER_SLEEP=900
QPURGE_SLEEP=2000
QPACKAGER_SLEEP=300
QPREPACKAGER_SLEEP=300

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Overwrite Pull Files: Politica de escritura si el archivo se encuentra
#
# OVERWRITE_PULL_FILES=True  -> Sobreescribe de los arhivos si existen
# OVERWRITE_PULL_FILES=False -> No sobreescribe y usa el file actual
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
OVERWRITE_PULL_FILES=False

PULL_LIMIT_AVAILABLE=True

PULL_LIMIT="30M"

MAX_QUOTA=650

OPTIMIZE_PROFILES_WITH_BRAND=True

LOCAL_SMB_PATH_ROUND_ROBIN=True

ZONE="NEPE-TEST"

