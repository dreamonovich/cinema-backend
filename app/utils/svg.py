import io
from uuid import uuid4

from lxml import etree

from app.cinema.models import Seat


def process_scheme(file, tag_names=('rect', 'circle', 'path', "ellipse")):
    tree = etree.parse(file)
    root = tree.getroot()

    ns = {'svg': 'http://www.w3.org/2000/svg'}
    seats = []
    for tag in tag_names:
        for elem in root.findall(f'.//svg:{tag}', ns):
            uuid = uuid4()
            row, col = elem.get("id").split("-")
            seats.append(
                Seat(
                    id=uuid,
                    row=row,
                    column=col
                )
            )

            elem.set('id', str(uuid))
            elem.set('fill', "white")

    etree.cleanup_namespaces(root)

    buffer = io.BytesIO()
    tree.write(buffer, pretty_print=True, encoding='utf-8', xml_declaration=True)
    buffer.seek(0)

    return buffer, seats
