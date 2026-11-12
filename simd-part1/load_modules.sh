module purge
module load base
module load vcs/S-2021.09-SP1

set SCRIPT_NAME = `lsof +p $$ | \grep -oE /.\*load_modules.sh`
set SCRIPT_PATH = `dirname $SCRIPT_NAME`
setenv PATH $SCRIPT_PATH/simulator/bin:$PATH
