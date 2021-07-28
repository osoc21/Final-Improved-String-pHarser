# Statistics

| Model name  | Source csv file | Training ratio | Error rate* | Token Error rate** |
| ------------- | ------------- | --- | --- | --- |
| Aphia.mod  | ExamplesAphia.csv  | 0.7 | 14.85% | 2.24% |
| all_examples.mod  | all_examples.csv | 0.7 | 72.02% | 25.44% | 
| AphiaFull.mod | aphiaFull.csv | 0.7 | 12.72% | 1.57% |

\* Ratio of citations with at least one mispredicted field

** Ratio of citation parts that were mispredicted

All_examples.mod consists of data from 2 different databases, it is mostly trained on one database and tested on the other, explaining its bad accuracy.