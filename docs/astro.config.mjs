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
						{ label: 'Entities', slug: 'guides/entities' },
						{ label: 'Identifiers', slug: 'guides/identifiers' },
						{ label: 'Reading data', slug: 'guides/reading' },
						{ label: 'Storing data', slug: 'guides/storing' },
						{ label: 'Provenance', slug: 'guides/provenance' },
						{ label: 'Counter handlers', slug: 'guides/counter_handlers' },
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
