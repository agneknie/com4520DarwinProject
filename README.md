# Is Less More? Quality, Quantity and Context in Idiom Processing with Natural Language Models

Adjacent code related to the paper presented in Joint Workshop on Multiword Expressions and Universal Dependencies ([MWE-UD 2024](https://multiword.org/mweud2024/)), 25th May, 2024. Co-located with [LREC-COLING 2024](https://lrec-coling-2024.org/) in Torino, Italy.

Originaly prepared as part of a Masters dissertation project on COM4520 at The University of Sheffield, with the name of "Is Less More? Idiom Detection with Generalised Natural Language Models".

Paper Authors: Agne Knietaite, Adam Allsebrook, Anton Minkov, Adam Tomaszewski, Norbert Slinko, Richard Johnson, Thomas Pickard, Aline Villavicencio, Dylan Phelps.

**Link to the paper: https://doi.org/10.48550/arXiv.2405.08497**

**Link to the NCSSB dataset: https://doi.org/10.15131/shef.data.25259722.v1**

![Paper Presentation Poster](Poster/Is_Less_More_Poster.png)

## Overview of the Repository

The code is divided into two sections, `Model` and `Dataset` related, following the structure of the adjacent report. The subdirectories are almost always self-contained and have their own `README` files for clarity.

### Model Related

- `src`: the base model code for fine-tune and pre-train scenarios. Equipped with model performance evaluation and visualisation techniques;
- `Jupiter Notebooks`: Jupiter notebooks, which allow to run the models as Jupiter Notebooks on Google Collab;
- `HPC Fine Tunning`: Information on how to schedule model training as jobs on other machines;
- `Paragraph External Context`: Gathering external context for the external knowledge enhanced model described in the paper

### Dataset Related

- `Data Augmentation`: Everything related to the data augmentation, used in the report;
- `Data Generation Parser`: Main parser, used for scrapping, adapting and constructing the datasets;
- `Datasets`: Base datasets used throughout the project;
- `Script For Scraping Text File` & `Web Scrapper & Crawler`: initial and later improved versions of data scraping and dataset forming tools.
