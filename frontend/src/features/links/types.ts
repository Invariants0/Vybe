export interface Link {
  id: number;
  user_id: number;
  short_code: string;
  original_url: string;
  title: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateLink {
  original_url: string;
  user_id: number;
  title?: string;
}
