#Linux:
#   chmod +x train_and_check.sh
#   ./train_and_check.sh examples.xml output.mod
#Windows: bash train_and_check.sh examples.xml output.mod
anystyle train $1 $2
anystyle -P $2 check gold.xml