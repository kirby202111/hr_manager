import client from './client'
import type { Skill } from '../types/skills'

export function getSkills() {
  return client.get<{ skills: Skill[] }>('/agent/skills')
}

export function enableSkill(name: string) {
  return client.post(`/agent/skills/${name}/enable`)
}

export function disableSkill(name: string) {
  return client.post(`/agent/skills/${name}/disable`)
}
