export interface PhotocaseOptionPublic {
  id: string
  label: string
}

export interface PhotocaseOptionAdmin extends PhotocaseOptionPublic {
  is_correct: boolean
  explanation: string
  order_index: number
}

export interface PhotocaseSubmitResult {
  is_correct: boolean
  selected_option_id: string
  key_signs: string | null
  next_steps: string | null
  options: PhotocaseOptionAdmin[]
}
