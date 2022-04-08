# Conference Statistics

Generate and plot statistics about papers at a conference

## Usage

```console
usage: stats.py [-h] [--views] [--normalize] [--bins BINS] [--database DATABASE]
                {attribute}

Conference Statistics

positional arguments:
  attribute             Attribute to plot
    {number_of_words_in_title,number_of_chars_in_title,number_of_words_in_abstract,number_of_authors,is_student_paper,submission_id,created_at}

optional arguments:
  -h, --help            show this help message and exit
  --views               Views to plot
                        [{all,accept_short,accept_long,accept,reject} ...]
  --normalize           Normalize before plotting
  --bins BINS           Number of bins
  --database DATABASE   Database File
```
