# Configuration file for Mizgra

# CHOICES

# Outputs choices
# local-ref-relations, usages-relations and broader-relations disabled by default (handled by CSV relations)
outputs_choices = {'filenames', 'nodes', 'metadata', 'member-relations', 'local-ref-relations', 'usages-relations',
                   'broader-relations', 'csv-relations', 'rdf-relations'}

disabled_outputs = {'local-ref-relations', 'usages-relations', 'broader-relations'}

# External format choices
rdf_format_choices = ('json-ld', 'hext', 'n3', 'nquads', 'nt', 'trix', 'turtle', 'xml')

# RELATIONS CONFIGURATION

# source tag name, MMLId attribute name, target XPath
# disabled by default (handled by CSV relations)
usages_relations = (('Theorem-Reference', 'MMLId', 'Theorem-Item'),

                    ('Attribute', 'absolutepatternMMLId', 'Attribute-Definition/Attribute-Pattern'),
                    ('Attribute', 'absolutepatternMMLId', 'Attr-Antonym/Attribute-Pattern'),
                    ('Attribute', 'absolutepatternMMLId', 'Attr-Synonym/Attribute-Pattern'),

                    ('Relation-Formula', 'absolutepatternMMLId', 'Predicate-Definition/Predicate-Pattern'),
                    ('Relation-Formula', 'absolutepatternMMLId', 'Pred-Antonym/Predicate-Pattern'),
                    ('Relation-Formula', 'absolutepatternMMLId', 'Pred-Synonym/Predicate-Pattern'),

                    ('Infix-Term', 'absolutepatternMMLId', 'Functor-Definition/InfixFunctor-Pattern'),
                    ('Circumfix-Term', 'absolutepatternMMLId', 'Functor-Definition/CircumfixFunctor-Pattern'),
                    ('Infix-Term', 'absolutepatternMMLId', 'Func-Synonym/InfixFunctor-Pattern'),
                    ('Circumfix-Term', 'absolutepatternMMLId', 'Func-Synonym/CircumfixFunctor-Pattern'),

                    ('Standard-Type', 'absolutepatternMMLId', 'Mode-Definition/Mode-Pattern'),
                    ('Standard-Type', 'absolutepatternMMLId', 'Mode-Synonym/Mode-Pattern'),)

# source, MMLId attribute name, target
# disabled by default (handled by CSV relations)
broader_relations = (('Structure-Definition/Structure-Pattern', 'absolutepatternMMLId', 'Ancestors/Struct-Type'),)

# source, MMLId attribute name, target
# not used now
# types_relations = (('Mode-Definition/Mode-Pattern', 'absolutepatternMMLId', 'Type-Specification/Standard-Type'),
#                    ('Mode-Definition/Mode-Pattern', 'absolutepatternMMLId', 'Clustered-Type/Standard-Type'),)
