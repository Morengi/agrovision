export type UserRole = 'student' | 'moderator' | 'admin'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
}

export const ROLE_LABELS: Record<UserRole, string> = {
  student: 'Студент',
  moderator: 'Модератор',
  admin: 'Администратор',
}
