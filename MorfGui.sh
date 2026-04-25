#
# Script to run the Morf Race program
#
# MorfRace <roster file name>
#   the default roster is morfrace.rst
#
export Morf_Data=./data/
export pythonpath=./
python MorfGUI/Gui.py $1
