// SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
//
// SPDX-License-Identifier: ISC

// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import rehypeExternalLinks from 'rehype-external-links';

export default defineConfig({
	site: 'https://opencitations.github.io',
	base: '/oc_ocdm/',
	integrations: [
		starlight({
			title: 'oc-ocdm',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/opencitations/oc_ocdm' }],
			sidebar: [
				{
					label: 'Guides',
					items: [
						{ label: 'GraphSet', slug: 'guides/graph_set' },
						{ label: 'Metadata', slug: 'guides/metadata' },
						{ label: 'Reading data', slug: 'guides/reading' },
						{ label: 'Storing data', slug: 'guides/storing' },
						{ label: 'Provenance', slug: 'guides/provenance' },
						{ label: 'Counter handlers', slug: 'guides/counter_handlers' },
					],
				},
				{
					label: 'Entities',
					items: [
						{ label: 'BibliographicResource', slug: 'entities/bibliographic_resource' },
						{ label: 'ResponsibleAgent', slug: 'entities/responsible_agent' },
						{ label: 'AgentRole', slug: 'entities/agent_role' },
						{ label: 'Identifier', slug: 'entities/identifier' },
						{ label: 'Citation', slug: 'entities/citation' },
						{ label: 'BibliographicReference', slug: 'entities/bibliographic_reference' },
						{ label: 'ResourceEmbodiment', slug: 'entities/resource_embodiment' },
						{ label: 'DiscourseElement', slug: 'entities/discourse_element' },
						{ label: 'ReferenceAnnotation', slug: 'entities/reference_annotation' },
						{ label: 'ReferencePointer', slug: 'entities/reference_pointer' },
						{ label: 'PointerList', slug: 'entities/pointer_list' },
					],
				},
			],
		}),
	],
	markdown: {
		rehypePlugins: [
			[rehypeExternalLinks, { target: '_blank', rel: ['noopener', 'noreferrer'] }],
		],
	},
});
