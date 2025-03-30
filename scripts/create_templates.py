pages = ['about', 'discography', 'album_pages']

content = """<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">

  <title>to: nujabes</title>

  <link rel="stylesheet" href="#">
</head>

<body>
  <audio id="bgMusic" autoplay loop>
        <source src="/static/music/Luv (sic) Grand Finale Instrumentals.mp3" type="audio/mpeg">
  </audio>
    
  <section class="main">

    </div>
  </section>

  <nav class="navbar">
    <a href="../index.html" class="nav-link">home</a>
    <a href="discography.html" class="nav-link">discography</a>
    <a href="about.html" class="nav-link">about</a>
  </nav>

  <script src="script.js"></script>
</body>

</html>


"""

for page in pages:

    with open(f"templates/{page}.html", "w") as file:

        file.write(content.format(page.capitalize()))