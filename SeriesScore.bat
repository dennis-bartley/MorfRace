rem SeriesScore <series name>
@rem
@rem  Script to Score a series
@rem
@rem  SeriesScore <series>
@rem     ... where series is the name of the series... eg comp, perf, etc
@rem
set Morf_Data=./data/
set pythonpath=./
python SeriesScore.py %1