# Didakta: Grammar for Annotation

**Didakta Grammar for Annotation** is a localizable grammar reference for the ancient Greek language, designed as a pedagogical resource for annotating syntactic features not covered in treebanks.

## About Didakta

Didakta has been developed by **Farnoosh Shamsian** at Leipzig University, primarily through rearrangement and reformulation of H. W. Smyth's _Greek Grammar for Colleges_ (1920), inspired by Jeffrey A. Rydberg-Cox's _Overview of Greek Syntax_ (2000). It incorporates insights from recent publications such as the _Cambridge Grammar of Classical Greek_ (Emde Boas et al., 2019).

### Link to various versions and translations:

Ferreira, A. D. (2024). Didakta Grammar for Annotation—Versão em Português. https://github.com/ProjetosAbertosClassicasDigitais/Didakta-br-portuguese/
Rahimi, F., Shamsian, F., & Smyth, H. W. (2024). Didakta Grammar for Annotation (Kurdish) [Dataset]. https://doi.org/10.5281/zenodo.11221442
Shamsian, F., & Smyth, H. W. (2023). Didakta Grammar for Annotation (English) [Dataset]. https://doi.org/10.5281/zenodo.11216456
Shamsian, F., & Smyth, H. W. (2024). Didakta Grammar for Annotation (Persian) [Dataset]. https://doi.org/10.5281/ZENODO.11216819

> **Note on vocabulary links.** The versions deposited on Zenodo, and the DOIs
> cited above, link every Greek word to the **Perseus** word-study tool
> (`perseus.tufts.edu/hopper/morph`). That service is legacy Perseus 4
> infrastructure: it rate-limits and returns HTTP 503 under sustained use, so in
> practice the links fail for anyone reading through a chapter. **In this
> repository every vocabulary link has been migrated to
> [Logeion](https://logeion.uchicago.edu/) (University of Chicago)**, which
> parses the inflected form and returns LSJ, Bailly, Pape, Middle Liddell and
> the other lexica it aggregates. The migration covers all formats — PDF, EPUB,
> DOCX, HTML, the split entries and the TEI XML — in all three languages.
> Citations still point at Perseus, which hosts the texts, but now over HTTPS.
> The Zenodo deposits are unchanged and remain the citable versions of record.

### Links to related publications:

Shamsian, F., Crane, G., & Rahimi, F. (2024, June 5). Adapting Digital Annotations for Teaching Ancient Greek in Persian. DH Benelux 2024. https://2024.dhbenelux.org/wp-content/uploads/2024/05/DHB24_paper_Shamsian_Crane_Rahimi.pdf
Shamsian, F., Crane, G., Rahimi, F., & Ferreira, A. D. (2024). Localizing Ancient Greek Grammar and Annotations with Didakta. DH 2024.

### Key Features

- **Modular Design**: Each section is self-contained and can be used independently without relying on other sections
- **Flexible Organization**: Sections can be rearranged based on learner needs, course requirements, or project specifications
- **Accessibility-Focused**: Simplified language to minimize inaccuracies in machine translation
- **No Positive Language Transfer**: Explains grammatical concepts without assuming knowledge of other languages, particularly important for localization

### Supported Languages

- English
- Persian
- Kurdish
- Portuguese (soon to be added here from https://github.com/ProjetosAbertosClassicasDigitais/Didakta-br-portuguese/)

## Repository Contents

### Primary Files

- `didakta-{language}.md` - Main markdown version of the grammar in each language.
  Cleaned for reuse: hyperlinks and the table of contents are removed, and
  headings are proper markdown (`#`/`##`/`###`) with footnotes preserved.
- `didakta-{language}.xml` - TEI P5 edition, with a per-word vocabulary link on
  every example. Generated from the markdown and the HTML export; see
  [TEI editions](#tei-editions) below.
  The followings are downloaded from the Zenodo versions and are the basis of the markdown versions.
  Their vocabulary links have been repointed at Logeion
  (see [Vocabulary links](#vocabulary-links)); they are otherwise untouched, and
  the PDFs keep their original pagination:
- `didakta-{language}.html` - HTML format for web viewing
- `didakta-{language}.epub` - E-book format
- `didakta-{language}.pdf` - PDF version for printing from
- `didakta-{language}.docx` - Microsoft Word format

### Supporting files

- `didakta-betacode.json` - the betacode-to-Greek mapping recovered from the
  original HTML exports, 2,070 forms. It is what each old Perseus URL referred
  to, kept so the migration stays reproducible after the betacode itself is gone
  from the files.

## TEI editions

`didakta-english.xml`, `didakta-persian.xml` and `didakta-kurdish.xml` are TEI P5
encodings of the three grammars, validated against `tei_all`. They are generated
from the two published formats together: the text comes from the markdown, and
the link structure from the HTML export.

How the grammar is encoded:

| Content | TEI |
| --- | --- |
| Chapter (a case, tense, voice, mood…) | `<div type="chapter" xml:id="ch01">` … `ch24` |
| Grammar entry (`§GenPart. Partitive`) | `<div type="entry" xml:id="GenPart">` with `<head><label>§GenPart</label> …` |
| Greek example with citation | `<cit type="example">` → `<quote xml:lang="grc">` + `<bibl>` |
| Its translation | nested `<cit type="translation">` → `<quote>` |
| Greek word, linked to Logeion | `<ref target="https://logeion.uchicago.edu/ταῦτα"><w>ταῦτα</w></ref>` |
| Word highlighted in an example | `<w rend="bold">`, or `<hi rend="bold">` outside a quotation |
| Citation, linked to the passage | `<bibl><ref target="…/hopper/text?doc=…">Xen. Anab. 1.2.3</ref></bibl>` |
| Footnote | `<note place="foot" n="7" xml:id="fn-7">`, inline at the point of reference |
| Greek quoted inside running prose | `<foreign xml:lang="grc">`, its words linked as above |
| References | `<back><div type="bibliography"><listBibl>` |

**Entry identifiers are the same in all three languages**, so the editions line up
entry by entry — `//div[@xml:id='GenPart']` is the partitive genitive in each file.
This makes the TEI versions usable as a parallel corpus, as an annotation
vocabulary (the Didakta tag is the `xml:id`), or as input to a TEI publishing
pipeline. Each file currently holds 24 chapters, 129 entries and ~650 Greek
examples with translations.

### Vocabulary links

The markdown cleanup removed the hyperlinks. The TEI files put them back: every
Greek word is tokenised as a `<w>` and linked to its vocabulary entry, and every
citation is linked to the passage in the Perseus Digital Library.

This covers the Greek quoted in running prose as well as the examples, so the
`<foreign>` phrases are linked word by word too — something the Zenodo exports
never did:

| | examples | running prose | total |
| --- | --- | --- | --- |
| English | 3,309 | 438 (281 phrases) | **3,747** |
| Persian | 3,296 | 424 (327 phrases) | **3,720** |
| Kurdish | 3,311 | 402 (303 phrases) | **3,713** |

plus 648 / 646 / 648 passage links. All three files validate against `tei_all`.

The Greek is tokenised from the markdown itself, so the vocabulary links do not
depend on the export at all. The export is still read for the citation links, and
examples are matched between the two files by their Greek text rather than by
position; an example the export does not cover keeps its vocabulary links and is
written without a citation link. `E. Fr. 632` and `Men. Sent. 11` have no passage
link because Perseus does not host those texts.

#### Why Logeion, and not Perseus

The export links each word to the Perseus hopper word-study tool. The hopper is
legacy Perseus 4 infrastructure; it still answers an occasional click, but it
rate-limits hard and returns HTTP 503 under sustained use, so a reader working
through a chapter hits dead links. All vocabulary links therefore point at
[Logeion](https://logeion.uchicago.edu/) instead, which parses the inflected form
and returns LSJ, Bailly 2024, Pape, Middle Liddell, Cunliffe, Autenrieth,
Grieks-Nederlands and Μορφώ together with corpus frequency.

The hopper URLs carry the word in betacode, and a few of those transliterations
are wrong in the export itself — this is what previously left `τραγῳδοῖς` and
`πέντε` pointing at the wrong form. (The recovered mapping has it in black and
white: the export encoded `τραγῳδοῖς` as `oagw|doi=s`, writing `o` for `tr`.)
Logeion targets are built from the Greek word as it is printed, so those errors
do not survive the migration. Elided forms are passed through unchanged: Logeion
falls back to the nearest alphabetic form, so `μήτ᾽` lands on the entry for
`μήτε`.

Citations still point at Perseus, which hosts the texts, upgraded from `http` to
`https` (the hopper serves HTTPS but does not redirect to it). Moving citations
to the Scaife Viewer would need a hand-checked `abbreviation → CTS URN` table for
roughly 70 works and has not been done.

#### How the migration was done

The TEI editions carry Logeion links from the start. The files downloaded from
Zenodo were rewritten in place, one format at a time.

The betacode-to-Greek mapping was learned from the HTML exports themselves, where
each link's anchor text is the word as printed, so no link was rewritten on a
guess; anything unresolvable was left alone and reported. That mapping is kept in
`didakta-betacode.json` so the migration stays checkable now that the betacode is
gone from the files. PDF pagination, EPUB and DOCX structure, and everything
other than the link targets are exactly as published.

## Usage

1. **Online**: Use the HTML versions for interactive reading, with a Logeion
   lookup on every Greek word
2. **Offline**: Download the EPUB or PDF formats for reading on e-readers or tablets
3. **Development**: Use the markdown files for editing or integration into other projects
4. **Interchange**: Use the TEI XML files for annotation tooling, parallel-text work, or digital-edition pipelines
5. **Split Entries**: Access individual concepts from the split-entries folders for focused learning. More coming on that front soon!

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
