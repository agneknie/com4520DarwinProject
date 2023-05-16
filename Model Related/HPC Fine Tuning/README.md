# Model Fine-Tuning Job Scheduling
The code provided in this folder is adapted to fine-tune the model on external, high performance computers. The initial guide uses internal University of Sheffield systems, which are not accessible to the public. However, the following is left for reference, as it explains how such jobs could be created on similar systems.

## Configuring the Job

In the repo there is a script called `hpc/fine_tune.sh` that configures the HPC environment and then trains the model using the `hpc/fine_tune_model.py` python script. 

1. Open `hpc/fine_tune.sh` in your editor.

> The `SBATCH` commands at the top of the file are used by `SLURM`, the bessemer job manager. 

2. You will want to change the email settings to your own email, and you may wish to remove the `BEGIN` and `END` mail types to reduce spam. 
3. You should change the job name to reflect what model is being trained. This will be used in the output file, making it easier to identify if anything goes wrong.
4. You can also change RAM, CPU and GPU config here, though the defaults should work fine.

>Note: the $dir variable refers to your personal home directory.

5. Next you should edit the arguments passed to the python file on the last line to whatever your job required.
   
> Command line arguments:
>
>| Argument | Description |
>| :--- | :---: |
>| --en | Use the English data, this should always be included |
>| --pt | Use the portuguese data, this should not be used |
>| --tokenize-idioms | Tokenize idioms, this should always be included |
>| --num-epochs | Number of epochs |
>| --batch-size | Batch size |
>| --seed | Random seed for reproducibility |
>| --include-para-context | Include the next and previous sentences |
>| --base-model | Path to the base model folder |
>| --train-file | Path to the train data csv |
>| --dev-path | Path to the dev data, this should not need to be changed |
>| --output-path | Path to save the model at, remember to change between jobs so you don't overwrite your model! |

6. Now your bash script is ready! Transfer it to the HPC using `scp`. Edits can also be made on the HPC directly using `nano` or `vim`.
