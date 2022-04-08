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

## Attributes

* `created_at`
* `submission_id`
* `number_of_authors`
* `number_of_words_in_title`
* `number_of_chars_in_title`
* `number_of_words_in_abstract`
* `is_student_paper`

## Views

Attributes can be plotted for any of the five views of the dataframe,

* `all`: All papers at the conference
* `accept_short`: Papers that were accepted as a short papers (`status == "Short"`)
* `accept_long`: Papers that were accepted as a long papers (`status == "Long"`)
* `accept`: Papers that were accepted (`status in ["Short", "Long"]`)
* `reject`: Papers that were rejected (`status in ["Reject", "Desk Reject"]`)