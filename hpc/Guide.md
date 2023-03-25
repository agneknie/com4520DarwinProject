# Fine tuning on the HPC 

(This all should work for bessemer, I have not looked into sharc)

## Logging on to the HPC

If you do not already have access to the HPC, follow the instructions [here](https://docs.google.com/document/d/1BbTYySt4zOfH6xMyPEcKCH3facYy3Hxe-KngToGHH0g/edit?usp=sharing).

[This guide](https://docs.hpc.shef.ac.uk/en/latest/hpc/connecting.html#connecting-to-a-cluster-using-ssh) is summarised:
1. Connect to the VPN
2. ssh into the HPC using the command `ssh -X $user@bessemer.shef.ac.uk`,  
   e.g. `ssh -X aca19aa@bessemer.shef.ac.uk`. You should be prompted for your password and duo 2FA.
3. You are now accessing the HPC via a login node, which has limited processing power but can be used to queue jobs.

Everyone has their own home directory under `/home/$user/` which is where we will store all of our data. 

## Uploading the base model and training data

In order to train our model on the HPC we need to upload the base model and any training data we want to use, as we will not be able access the google drive. This can be done using the `scp` command.

1. Download the base model, which is on the drive at `Models/base_model_tokenized`. Download the whole folder as a `.zip`.
2. Download any training data CSVs you want to use from the drive.

>The `scp` command works like this:
>
>`scp some/local/file.txt $user@bessemer.shef.ac.uk:some/remote/file.txt`
>
>The bessemer address is the same as before, except that it is followed by `:` and a filepath. This path is relative to our own home directory.

3. Upload the base model and training data using `scp` (this should be done from a terminal on your local machine, not in the ssh terminal).  
   e.g. `scp base_model_tokenized.zip aca19aa@bessemer.shef.ac.uk:base_model_tokenized.zip`
4. Any zip files can be unzipped on the HPC using `unzip $filename.zip`

## Configuring the job

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

## Queueing the job

1. You can queue the job using `sbatch fine_tune.sh`
2. The job should now appear when you request a lists of all your jobs using `squeue --user=$user` or the shorthand `squeue --me`.
3. You can get an estimated start time using `squeue --me --start`, though I have found that the job is usually run faster than this. 

## Retrieving the model

If everything has worked correctly we should now have a model successfully trained on the HPC! We can send it to our local machine using `zip` and `scp`

1. Zip the model folder using `zip -r model_name.zip model_name`

> The `scp` command we used earlier was transferring from local to remote, but scp does not actually care which direction the file is being transferred in! So we can just switch the local and remote paths to download from the HPC.

1. Transfer the zip file using `scp` on your local machine. `scp $user@bessemer.shef.ac.uk:model_name.zip model_name.zip`
2. Now our model is home safe and we can upload it to the drive.

### Note on model enhancements

I am assuming for the model enhancements (gloss/ paracomet) we are generating a copy of every train file with the enhancement included, so including the enhancement is just a matter of changing the `--train-file`.
