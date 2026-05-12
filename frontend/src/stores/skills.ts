import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Skill } from '../types/skills'
import * as skillsApi from '../api/skills'

export const useSkillsStore = defineStore('skills', () => {
  const skills = ref<Skill[]>([])
  const loading = ref(false)

  async function fetchSkills() {
    loading.value = true
    try {
      const { data } = await skillsApi.getSkills()
      skills.value = data.skills
    } catch (e) {
      console.error('获取技能列表失败:', e)
    }
    loading.value = false
  }

  async function toggleSkill(name: string, enabled: boolean) {
    try {
      if (enabled) {
        await skillsApi.enableSkill(name)
      } else {
        await skillsApi.disableSkill(name)
      }
      const skill = skills.value.find(s => s.name === name)
      if (skill) skill.enabled = enabled
    } catch { /* ignore */ }
  }

  return { skills, loading, fetchSkills, toggleSkill }
})
