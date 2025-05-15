import fitz

#filename = "../Klageschrift.pdf"

class Address:
	def __init__(self, street, city, po_box = None):
		self.street = street
		self.city = city
		self.po_box = po_box

	def print(self):
		if self.po_box:
			print("Address: {}, {}, {}".format(self.street, self.po_box, self.city))
		else:
			print("Address: {}, {}".format(self.street, self.city))


class Entity:
	def __init__(self, name, address, role = None, additional = None, representative = None):
		self.name = name
		self.address = address
		self.role = role
		self.additional = additional
		#additional is either firm or profession
		self.representative = representative

	def print(self):
		if self.role:
			print(self.role)
		print(self.name)
		if self.additional:
			print(self.additional)
		self.address.print()
		if self.representative:
			print("Represented by:")
			self.representative.print()

class Header:
	def __init__(self, court, plaintiff, defendant):
		court.role = "Court"
		plaintiff.role = "Plaintiff"
		defendant.role = "Defendant"
		self.court = court
		self.plaintiff = plaintiff
		self.defendant = defendant

	def print(self):
		self.court.print()
		print("------------")
		self.plaintiff.print()
		print("------------")
		self.defendant.print()


# court_address = Address("Baumleingasse 5", "4001 Basel", "Postfach 964")
# court = Entity("Zivilgericht Basel-Stadt", court_address)
# plaintiff_address = Address("Scheideggstrasse 66", "8002 Zurich")
# plaintiff_lawyer = Entity("Dr. Sandro Maurer", Address("Erwenbergstrasse 51", "4410 Liestal", "Postfach"), role = "Representative")
# plaintiff = Entity("Muller & Janser AG", plaintiff_address, representative = plaintiff_lawyer)
# defendant_address = Address("Klingentalstrasse 41", "4057 Basel", "Postfach 120")
# defendant_lawyer = Entity("Dr. Mark Sacher", Address("Freie Strasse 45", "4001 Basel", "Postfach"), role = "Representative", firm = "Sacher Rechtsanwalte")
# defendant = Entity("Peter Meister", defendant_address, representative = defendant_lawyer, profession = "Werbegrafiker")
# header = Header(court, plaintiff, defendant)
# header.print()

# def get_lines(filename):
# 	reader = PdfReader(filename)
# 	text = []

# 	for page in reader.pages:
# 		text.extend(page.extract_text().splitlines())
# 	return [line.strip() for line in text if line.strip()]

def is_bold(span):
	return "Bold" in span["font"]

def get_spans(filename):
	doc = fitz.open(filename)
	spans = []
	for page in doc:
		for block in page.get_text("dict")["blocks"]:
			for line in block.get("lines", []):
				for span in line.get("spans", []):
					if span["text"].strip():
						spans.append(span)
	return (spans)

def get_court(spans):
	lines = []
	collecting = False
	for span in spans:
		text = span["text"].strip()
		if "An das" in text:
			collecting = True
			continue
		if collecting:
			lines.append(text)
		if collecting and text[0:4].isdigit():
			collecting = False
			break
	return (Entity(lines[0], Address(lines[1], lines[3], po_box = lines[2])))

def get_po_box(lines):
	for line in lines:
		if "Postfach" in line:
			return (line)

def build_person(line, role, representative = None):
	lines = line.split(", ")
	name = lines[0]
	po_box = get_po_box(lines)
	if len(lines) == 3:
		additional = None
		address = Address(lines[1], lines[2])
	elif len(lines) == 4 and po_box:
		additional = None
		address = Address(lines[1], lines[3], po_box = po_box)
	elif len(lines) == 4 and not po_box:
		additional = lines[1]
		address = Address(lines[2], lines[3])
	elif len(lines) == 5:
		additional = lines[1]
		address = Address(lines[2], lines[4], po_box = po_box)
	return Entity(name, address, role, additional, representative)

def get_plaintiff(spans):
	first_line = ""
	second_line = ""
	collecting_first = False
	collecting_second = False
	for span in spans:
		text = span["text"]
		if "in Sachen" in text:
			collecting_first = True
			continue
		if "Klägerin" in text:
			collecting_first = False
			collecting_second = True
			continue
		if collecting_first:
			first_line += text
		if collecting_second and is_bold(span):
			break
		if collecting_second:
			second_line += text
	if second_line:
		lawyer = build_person(second_line[len("vertreten durch RA "):], "Representative")
	else:
		lawyer = None
	plaintiff = build_person(first_line, "Plaintiff", lawyer)
	return (plaintiff)

def get_defendant(spans):
	first_line = ""
	second_line = ""
	collecting_first = False
	collecting_second = False
	found_klagerin = False
	for span in spans:
		text = span["text"]
		if "Klägerin" in text:
			found_klagerin = True
			continue
		if found_klagerin and is_bold(span):
			collecting_first = True
			found_klagerin = False
			first_line += text
			continue
		if "Beklagter" in text:
			collecting_first = False
			collecting_second = True
			continue
		if collecting_first:
			first_line += text
		if collecting_second and is_bold(span):
			break
		elif collecting_second:
			second_line += text
	if second_line:
		lawyer = build_person(second_line[len("vertreten durch RA "):], "Representative")
	else:
		lawyer = None
	defendant = build_person(first_line, "Defendant", lawyer)
	return (defendant)

def get_header(filename):
	spans = get_spans(filename)
	return Header(get_court(spans), get_plaintiff(spans), get_defendant(spans))
