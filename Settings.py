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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pull Files: Intenta traer los archivos a un repositorio local
#
# Nota: El repositorio Remoto debe estar Montado por NFS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
PULL_FILES=True

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pull Error: Si Tolera Errores el traer los Files
#
# PULL_ERROR=True  -> Si no puede traer los archivos igual sigue el proceso
# PULL_ERROR=False -> Si no puede traer los archivos Falla
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
PULL_ERROR=False

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Overwrite Pull Files: Politica de escritura si el archivo se encuentra
#
# OVERWRITE_PULL_FILES=True  -> Sobreescribe de los arhivos si existen
# OVERWRITE_PULL_FILES=False -> No sobreescribe y usa el file actual
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
OVERWRITE_PULL_FILES=False


