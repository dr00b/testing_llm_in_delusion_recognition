import spacy
nlp = spacy.load('en')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

# You're done. You can now use NeuralCoref as you usually manipulate a SpaCy document annotations.
a = "My dad passed away last summer after suffering from the behavioral variant FTD, he was older when he was diagnosed but he probably had it longer but we probably missed a lot of signs over the years. When the symptoms really started getting bad that's when my dad's doctor ordered an MRI and we learned that the frontal part of his brain was shrinking and in atrophy.  For my dad, from diagnosis to death it took less than two years, a year and nine and a half months to be exact.    As another poster mentioned I wrote a journal of everything he went through and it was challenging for sure as my mother and I were his caregivers the entire time.  If there was one blessing it was that he never lost his memory of who my mom and I were so that was a good thing.  I could write a book here on what we went through with this disease but almost seven months since his passing, I wish I could take care of him for just one more day."
doc = nlp("My sister has a dog. She loves him.")

print(doc._.has_coref)
print(doc._.coref_clusters)
