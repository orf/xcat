xquery version "1.0";
  <html>
    <head>
      <title>A list of books</title>
    </head>
    <body>
      <h1>A list of books</h1>
      <p>Here are some interesting books:</p>
      <ul> {
        for $b in //BOOKS/ITEM
        order by $b/TITLE return
          <li><i> { string($b/TITLE) } </i> by { string($b/AUTHOR) } </li>
      } </ul>
    </body>
  </html>
    
