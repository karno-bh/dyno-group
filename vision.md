# What is this about?

As part of my job I always encounter a task when there is a need to create a groups view of denormalized
set of data. First, grouped data are easier to analyze. Also, sometimes it is needed as a part of code.
Yes, there are different solutions for such problem. However, most of the time what people do is writing
from scratch more or less the same logic again and again. Thus, I decided to create a tool that will be
able to solve the grouping of the denormalized set of data.

# Project Goals

1. Create a tool that will produce denormalized set of data (i.e, from CSV -> JSON)

   Possible sub-goals:

   1. Dataset will may be huge, so need take into account huge data-sets.
   2. Easy to use definitions of what and how should be grouped
   3. UI to be a kind of visual tool

2. Possible extensions

   1. The tool should be able to generate a code for more or less known languages to be useful for embedding (and
      not only for Python)
   2. The tool should be easy extended to generate a code for different languages (C, Java, Python?)
