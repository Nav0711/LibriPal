import React, { useState, useEffect } from 'react';
import { Save, Bell, MessageSquare, Calendar } from 'lucide-react';

const UserProfile = ({ apiCall }) => {
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    email: '',
    telegram_chat_id: '',
    preferences: {
      email_reminders: true,
      telegram_reminders: false,
      reminder_days: [3, 1],
      recommendation_frequency: 'weekly'
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await apiCall('/profile');
        setProfile({
          ...data,
          preferences: data.preferences || {
            email_reminders: true,
            telegram_reminders: false,
            reminder_days: [3, 1],
            recommendation_frequency: 'weekly'
          }
        });
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [apiCall]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await apiCall('/profile', {
        method: 'PUT',
        body: JSON.stringify({
          first_name: profile.first_name,
          last_name: profile.last_name,
          telegram_chat_id: profile.telegram_chat_id,
          preferences: profile.preferences
        })
      });
      alert('Profile updated successfully!');
    } catch (error) {
      alert('Error updating profile: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const updatePreference = (key, value) => {
    setProfile(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <h1>👤 User Profile</h1>

      <form onSubmit={handleSave} className="profile-form">
        {/* Basic Information */}
        <div className="form-section">
          <h2>Basic Information</h2>
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input
                type="text"
                value={profile.first_name || ''}
                onChange={(e) => setProfile(prev => ({ ...prev, first_name: e.target.value }))}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input
                type="text"
                value={profile.last_name || ''}
                onChange={(e) => setProfile(prev => ({ ...prev, last_name: e.target.value }))}
                className="form-input"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={profile.email || ''}
              disabled
              className="form-input disabled"
            />
            <small>Email is managed by your account provider</small>
          </div>

          <div className="form-group">
            <label>Telegram Chat ID (for bot notifications)</label>
            <input
              type="text"
              value={profile.telegram_chat_id || ''}
              onChange={(e) => setProfile(prev => ({ ...prev, telegram_chat_id: e.target.value }))}
              placeholder="e.g., @username or chat ID"
              className="form-input"
            />
            <small>Optional: Enable Telegram notifications by setting your chat ID</small>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="form-section">
          <h2><Bell className="section-icon" /> Notification Preferences</h2>
          
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={profile.preferences.email_reminders}
                onChange={(e) => updatePreference('email_reminders', e.target.checked)}
              />
              <span>Email Reminders</span>
            </label>
            <small>Receive email notifications for due dates and reservations</small>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={profile.preferences.telegram_reminders}
                onChange={(e) => updatePreference('telegram_reminders', e.target.checked)}
                disabled={!profile.telegram_chat_id}
              />
              <span>Telegram Reminders</span>
            </label>
            <small>Receive Telegram bot notifications (requires Telegram Chat ID)</small>
          </div>

          <div className="form-group">
            <label>Reminder Days Before Due Date</label>
            <div className="reminder-days">
              {[1, 2, 3, 5, 7].map(day => (
                <label key={day} className="checkbox-label inline">
                  <input
                    type="checkbox"
                    checked={profile.preferences.reminder_days.includes(day)}
                    onChange={(e) => {
                      const days = profile.preferences.reminder_days;
                      if (e.target.checked) {
                        updatePreference('reminder_days', [...days, day].sort((a, b) => b - a));
                      } else {
                        updatePreference('reminder_days', days.filter(d => d !== day));
                      }
                    }}
                  />
                  <span>{day} day{day > 1 ? 's' : ''}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* AI Preferences */}
        <div className="form-section">
          <h2><MessageSquare className="section-icon" /> AI Assistant Preferences</h2>
          
          <div className="form-group">
            <label>Recommendation Frequency</label>
            <select
              value={profile.preferences.recommendation_frequency}
              onChange={(e) => updatePreference('recommendation_frequency', e.target.value)}
              className="form-select"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="never">Never</option>
            </select>
          </div>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary btn-large"
          disabled={saving}
        >
          <Save className="btn-icon" />
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>

      {/* Instructions */}
      <div className="profile-help">
        <h3>📱 How to set up Telegram notifications:</h3>
        <ol>
          <li>Search for our bot "@LibriPalBot" on Telegram</li>
          <li>Start a conversation with the bot</li>
          <li>Send "/start" to get your chat ID</li>
          <li>Copy the chat ID and paste it in the field above</li>
        </ol>
      </div>
    </div>
  );
};

export default UserProfile;