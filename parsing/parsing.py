import fitz

filename = "../Klageschrift.pdf"

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

class Argument:
	def __init__(self, statement, evidence = None):
		self.statement = statement
		self.evidence = evidence

	def print(self):
		print("Statement:")
		print(self.statement)
		if self.evidence:
			print("Evidence:")
			for obj in self.evidence:
				print(obj)

	def to_string(self):
		result = self.statement + "\n"
		for evidence in self.evidence:
			result += f" - {evidence}\n"
		return result.strip()

class Justification:
	def __init__(self, formalities, jurisdiction, facts):
		self.formalities = formalities
		self.jurisdiction = jurisdiction
		self.facts = facts
	
	def print(self):
		print("I. Formelles")
		for arg in self.formalities:
			arg.print()
		print("II. Zuständigkeit")
		for arg in self.jurisdiction:
			arg.print()
		print("III. Materielles")
		for arg in self.facts:
			arg.print()
	
	def to_string(self):
		result = "I. Formelles\n"
		for arg in self.formalities:
			result += arg.to_string() + "\n"
		result += "II. Zuständigkeit\n"
		for arg in self.jurisdiction:
			result += arg.to_string() + "\n"
		result += "III. Materielles\n"
		for arg in self.facts:
			result += arg.to_string() + "\n"
		return result.strip()

class Info:
	def __init__(self, header, claims, justification):
		self.header = header
		self.claims = claims
		self.justification = justification

	def print(self, print_header = False):
		if print_header:
			print("Header:")
			self.header.print()
		print("Rechtsbegehren:")
		for i, claim in enumerate(self.claims):
			print("{}. {}".format(i + 1, claim))
		print("Begründung:")
		self.justification.print()

	def to_string(self, print_header = False):
		result = ""
		if print_header:
			result += "Header:\n"
			result += self.header.to_string() + "\n\n"
		result += "Rechtsbegehren:\n"
		for i, claim in enumerate(self.claims):
			result += f"{i + 1}. {claim}\n"
		result += "\nBegründung:\n"
		result += self.justification.to_string()
		return result.strip()

	def to_file(self, filepath, print_header = False):
		with open(filepath, "w", encoding = "utf-8") as f:
			f.write(self.to_string(print_header))

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
		if collecting_second and "gegen" in text:
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

def get_header(spans):
	return Header(get_court(spans), get_plaintiff(spans), get_defendant(spans))

def get_claims(spans):
	claims = []
	line = ""
	collecting = False
	for span in spans:
		text = span["text"]
		if "Rechtsbegehren" in text:
			collecting = True
			continue
		if collecting and text.strip()[0].isdigit():
			if line != "":
				claims.append(line)
			line = ""
			continue
		if collecting and "Begründung" in text:
			claims.append(line)
			break
		if collecting:
			line += text
	return claims

def get_arguments(spans, upper_bound, lower_bound):
	formalities = []
	statement = ""
	evidence = ""
	evidence_array = []
	collecting = False
	in_statement = False
	in_evidence = -1

	for span in spans:
		text = span["text"].strip()

		if collecting and (lower_bound in text):
			break
		if upper_bound in text:
			collecting = True
			in_statement = True
			continue
		if in_statement:
			if "BO:" in text:
				in_statement = False
				in_evidence = 2
				continue
			elif statement and in_evidence == 0:
				formalities.append(Argument(statement.strip(), evidence_array))
				evidence_array = []
				statement = ""
				in_evidence = -1
			statement += " " + text
		if in_evidence > 0:
			evidence += " " + text
			in_evidence -= 1
			if in_evidence == 0:
				evidence_array.append(evidence.strip())
				evidence = ""
				in_evidence = False
				in_statement = True
				continue
	if evidence:
		evidence_array.append(evidence.strip())
	if statement:
		formalities.append(Argument(statement.strip(), evidence_array))
	return (formalities)
	
def get_justification(spans):
	formalities = get_arguments(spans, "Formelles", "II")
	jurisdiction = get_arguments(spans, "Zuständigkeit", "III")
	facts = get_arguments(spans, "Materielles", "Zinsanspruch")
	return Justification(formalities, jurisdiction, facts)

def get_info(filename):
	spans = get_spans(filename)
	return Info(get_header(spans), get_claims(spans), get_justification(spans))

# info = get_info(filename)
# info.print()
# info.to_file("test")