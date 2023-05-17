# Is Less More? Idiom Detection with Generalised Natural Language Models

Adjacent code related to the report/publication, prepared as a Masters dissertation project on COM4520 at The University of Sheffield.

Created by: Agne Knietaite, Adam Allsebrook, Anton Minkov, Adam Tomaszewski, Norbert Slinko, Richard Johnson.

Supervised by: Aline Villavicencio.

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