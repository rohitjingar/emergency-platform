import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { volunteersAPI } from '../../api/volunteers'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Alert from '../../components/common/Alert'
import { CheckCircle } from 'lucide-react'

const SKILLS = [
  { value: 'medical', label: 'Medical', description: 'First aid, CPR, medical emergencies' },
  { value: 'fire', label: 'Fire', description: 'Fire suppression, rescue from fire' },
  { value: 'flood', label: 'Flood', description: 'Water rescue, flood response' },
  { value: 'rescue', label: 'Rescue', description: 'General rescue operations' },
]

export default function VolunteerRegister() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    skills: [],
    radius_km: 10,
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)

  const { data: profileData, isLoading: profileLoading } = useQuery({
    queryKey: ['volunteer-profile'],
    queryFn: () => volunteersAPI.getProfile(),
    retry: false,
  })

  useEffect(() => {
    if (profileData?.data) {
      setFormData({
        skills: profileData.data.skills || [],
        radius_km: profileData.data.radius_km || 10,
      })
      setIsEditMode(true)
    }
  }, [profileData])

  const mutation = useMutation({
    mutationFn: (data) => isEditMode 
      ? volunteersAPI.updateProfile(data) 
      : volunteersAPI.register(data),
    onSuccess: () => {
      setSuccess(true)
      queryClient.invalidateQueries(['volunteer-profile'])
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Operation failed')
    },
  })

  const toggleSkill = (skill) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill],
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (formData.skills.length === 0) {
      setError('Please select at least one skill')
      return
    }

    mutation.mutate(formData)
  }

  if (profileLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto">
        <Card className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            {isEditMode ? 'Profile Updated!' : 'Registration Complete!'}
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {isEditMode 
              ? 'Your volunteer profile has been updated.' 
              : 'Your volunteer profile has been created.'}
          </p>
          <Button onClick={() => navigate('/volunteer')}>
            Back to Dashboard
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {isEditMode ? 'Edit Volunteer Profile' : 'Volunteer Registration'}
      </h1>

      {error && (
        <Alert type="error" className="mb-6">
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Your Skills</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Select all skills you can help with</p>
          <div className="grid md:grid-cols-2 gap-3">
            {SKILLS.map((skill) => (
              <label
                key={skill.value}
                className={`
                  flex items-start p-4 border rounded-lg cursor-pointer transition-colors
                  ${formData.skills.includes(skill.value)
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:border-gray-600'
                  }
                `}
              >
                <input
                  type="checkbox"
                  checked={formData.skills.includes(skill.value)}
                  onChange={() => toggleSkill(skill.value)}
                  className="sr-only"
                />
                <div className="flex items-center h-5 mr-3 mt-0.5">
                  <div className={`
                    w-5 h-5 rounded border-2 flex items-center justify-center transition-colors
                    ${formData.skills.includes(skill.value)
                      ? 'bg-primary-600 border-primary-600'
                      : 'border-gray-300 dark:border-gray-600'
                    }
                  `}>
                    {formData.skills.includes(skill.value) && (
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-900 dark:text-white">{skill.label}</span>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{skill.description}</p>
                </div>
              </label>
            ))}
          </div>
        </Card>

        <Card className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Response Radius</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            How far are you willing to travel to help? ({formData.radius_km} km)
          </p>
          <input
            type="range"
            min={1}
            max={100}
            value={formData.radius_km}
            onChange={(e) => setFormData({ ...formData, radius_km: parseInt(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 mt-2">
            <span>1 km</span>
            <span>100 km</span>
          </div>
        </Card>

        <div className="flex justify-end gap-4">
          <Button type="button" variant="secondary" onClick={() => navigate('/volunteer')}>
            Cancel
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            {isEditMode ? 'Update Profile' : 'Complete Registration'}
          </Button>
        </div>
      </form>
    </div>
  )
}
