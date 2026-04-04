export interface Link {
  id?: string;
  shortCode: string;
  originalUrl: string;
  title?: string;
  clicks: number;
  status: 'active' | 'expired' | 'disabled';
  createdAt?: Date;
  expiresAt?: Date | null;
}

export interface CreateLink {
  originalUrl: string;
  customSlug?: string;
  expiresAt?: Date;
}
