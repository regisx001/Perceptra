import { z } from "zod";

export const schema = z.object({
	id: z.number(),
	filename: z.string(),
	category: z.string(),
	thumbnail: z.string().optional(),
	descriptorType: z.string(),
	vectorDim: z.number(),
	similarityScore: z.number(),
	status: z.enum(["Indexed", "Processing", "Optimized", "Pending"]),
	feedbackWeight: z.string(),
	updatedAt: z.string(),
});

export type Schema = z.infer<typeof schema>;
