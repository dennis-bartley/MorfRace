rem MorfGui <optional roster file>
@rem
@rem  Script to run the Morf Race program
@rem
@rem  MorfRace <roster file name>
@rem   the default roster is morfrace.rst
@rem
set Morf_Data=./data/
set pythonpath=./
python MorfGUI/Gui.py %1
