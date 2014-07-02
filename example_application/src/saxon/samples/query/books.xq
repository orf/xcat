xquery version "1.0";
declare copy-namespaces no-preserve, inherit;

for $b in //BOOKS/ITEM
order by string-length($b/TITLE) return
<book>
  <author> { $b/AUTHOR } </author>
  <title> { $b/TITLE } </title>
</book>