import glob
import subprocess
import os
import time
import urllib.parse
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from functions import *

import argparse

def run(name, url, out_dir, firefox_bin, geckodriver):

  os.makedirs(f"{out_dir}", exist_ok=True)
  os.makedirs(f"{out_dir}/\"Pagine da {name}\"", exist_ok=True)

  options = Options()
  options.add_argument("--headless")
  options.headless = True
  options.binary_location = firefox_bin

  service = Service(executable_path=geckodriver)

  print("accendendo firefox")
  driver = webdriver.Firefox(service=service, options=options)

  print("caricando la pagina")
  driver.get(url)
  print("sleep 5")
  time.sleep(5)

  print("scrolling")
  driver.find_element("tag name", "body").send_keys(Keys.PAGE_DOWN)
  print("sleep 3")
  time.sleep(3)

  seen_pages = {}
  last_new_pages = 0
  stuck_counter = 0

  print("entrando nel loop di scroll")
  while True:
      html = driver.page_source
      soup = BeautifulSoup(html, "html.parser")

      current_pages = soup.find_all(
          "div",
          id=lambda x: x and "pageContainer" in x
      )

      new_count = 0

      for p in current_pages:
          pid = p.get("id")

          if pid not in seen_pages:

              print("aspettando immagine, pagina: ", pid)
              try:
                src = WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script(f"""
                        const el = document.getElementById("{pid}");
                        if (!el) return null;

                        const img = el.querySelector("img");
                        if (!img) return null;

                        const s = img.getAttribute("src");

                        if (!s || s.length < 10 || s.startsWith("data:")) return null;

                        return s;
                    """)
                )
              except TimeoutException:
                break

              time.sleep(0.3)

              print("disponibile immagine, src:", src)

              fresh_el = driver.find_element("id", pid)
              html = driver.execute_script("return arguments[0].outerHTML;", fresh_el)
              p_bs = BeautifulSoup(html, "html.parser")

              seen_pages[pid] = p_bs

              new_count += 1
              print("preso:", pid)

      if new_count == 0:
          stuck_counter += 1
      else:
          stuck_counter = 0

      print("scrolling")

      driver.find_element("tag name", "body").send_keys(Keys.PAGE_DOWN)


      if stuck_counter > 5:
          print("breaking")
          break

  driver.quit()


  pages = list(seen_pages.values())

  pages = sorted(pages, key=page_id)

  driver = webdriver.Firefox(
      service=service,
      options=options
  )


  #si poteva fare prima ma il driver si incazza ...
  for i, page in enumerate(pages):

      page_html = str(page)

      svg_class = extract_single_svg_class(page)
      text_classes = extract_svg_text_classes(page)
      svg_style = build_svg_style(svg_class, text_classes)

      final_html = wrap_page(page_html, svg_style)

      out_path = os.path.join(f"{out_dir}/\"Pagine da {name}\"", f"page_{i}.html")

      abs_path = os.path.abspath(out_path)

      with open(abs_path, "w", encoding="utf-8") as f:
          f.write(final_html)

      driver.get(f"file://{abs_path}")

      print_options = PrintOptions()

      print_options.background = True
      print_options.orientation = "portrait" #non sono sicuro
      print_options.scale = 1

      pdf_data = driver.print_page(print_options)

      pdf_path = os.path.join(f"{out_dir}/\"Pagine da {name}\"", f"page_{i}.pdf")

      with open(pdf_path, "wb") as f:
          f.write(base64.b64decode(pdf_data))

      print("salvato pdf:", pdf_path)


  files = sorted(glob.glob(f"{out_dir}/\"Pagine da {name}\"/page_*.pdf"))

  output = f"{out_dir}/{name.replace('.pdf','')}.pdf"

  subprocess.run(
      ["pdfunite", *files, output],
      check=True
  )
  driver.quit()



if __name__ == "__main__":
  print("init")

  parser = argparse.ArgumentParser()

  parser.add_argument("--name", required=True)
  parser.add_argument("--url", required=True)
  parser.add_argument("--out_dir", default="pages_html")
  parser.add_argument("--firefox_bin", default="/usr/bin/firefox")
  parser.add_argument("--geckodriver", default="/home/ruben/Downloads/geckodriver")

  args = parser.parse_args()

  run(args.name, args.url, args.out_dir, args.firefox_bin, args.geckodriver)

