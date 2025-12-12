import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Grid,
  Avatar,
  IconButton,
  Divider,
  Alert,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  Storage as StorageIcon,
  Help as HelpIcon,
  PhotoCamera as CameraIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const Settings = () => {
  const [settings, setSettings] = useState({
    username: 'RoboLearner',
    email: 'user@example.com',
    notifications: true,
    emailUpdates: false,
    soundEnabled: true,
    autoSave: true,
    theme: 'light',
    language: 'en',
  });

  const [saveStatus, setSaveStatus] = useState(null);

  const handleSave = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleInputChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const SettingCard = ({ title, icon, children }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            {icon}
            <Typography variant="h6" sx={{ ml: 1 }}>
              {title}
            </Typography>
          </Box>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Settings
      </Typography>

      {saveStatus && (
        <Alert
          severity={saveStatus}
          sx={{ mb: 3 }}
          onClose={() => setSaveStatus(null)}
        >
          {saveStatus === 'success' ? 'Settings saved successfully!' : 'Failed to save settings. Please try again.'}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Settings */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Profile"
            icon={<PersonIcon color="primary" />}
          >
            <Box display="flex" alignItems="center" mb={3}>
              <Avatar
                sx={{ width: 80, height: 80, mr: 2, bgcolor: 'primary.main' }}
              >
                <PersonIcon sx={{ fontSize: 40 }} />
              </Avatar>
              <Box>
                <IconButton
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': { bgcolor: 'primary.dark' },
                  }}
                >
                  <CameraIcon />
                </IconButton>
                <Typography variant="caption" display="block">
                  Change Avatar
                </Typography>
              </Box>
            </Box>

            <TextField
              fullWidth
              label="Username"
              value={settings.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={settings.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              select
              fullWidth
              label="Language"
              value={settings.language}
              onChange={(e) => handleInputChange('language', e.target.value)}
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </TextField>
          </SettingCard>

          {/* Appearance Settings */}
          <SettingCard
            title="Appearance"
            icon={<PaletteIcon color="primary" />}
          >
            <TextField
              select
              fullWidth
              label="Theme"
              value={settings.theme}
              onChange={(e) => handleInputChange('theme', e.target.value)}
              sx={{ mb: 2 }}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </TextField>

            <Typography variant="body2" color="textSecondary" gutterBottom>
              Theme changes will be applied immediately
            </Typography>
          </SettingCard>
        </Grid>

        {/* Notifications & Preferences */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Notifications"
            icon={<NotificationsIcon color="primary" />}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={(e) => handleInputChange('notifications', e.target.checked)}
                />
              }
              label="Push Notifications"
              sx={{ mb: 2, width: '100%', justifyContent: 'space-between', ml: 0 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={settings.emailUpdates}
                  onChange={(e) => handleInputChange('emailUpdates', e.target.checked)}
                />
              }
              label="Email Updates"
              sx={{ mb: 2, width: '100%', justifyContent: 'space-between', ml: 0 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={settings.soundEnabled}
                  onChange={(e) => handleInputChange('soundEnabled', e.target.checked)}
                />
              }
              label="Sound Effects"
              sx={{ width: '100%', justifyContent: 'space-between', ml: 0 }}
            />
          </SettingCard>

          {/* Learning Preferences */}
          <SettingCard
            title="Learning Preferences"
            icon={<HelpIcon color="primary" />}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoSave}
                  onChange={(e) => handleInputChange('autoSave', e.target.checked)}
                />
              }
              label="Auto-save Progress"
              sx={{ mb: 2, width: '100%', justifyContent: 'space-between', ml: 0 }}
            />

            <Typography variant="body2" gutterBottom sx={{ mb: 2 }}>
              Preferred Learning Domains:
            </Typography>

            <Box display="flex" flexWrap="wrap" gap={1}>
              {['Programming', 'Robotics', 'AI/ML', 'Electronics'].map((domain) => (
                <Chip
                  key={domain}
                  label={domain}
                  variant="outlined"
                  color="primary"
                  sx={{ mb: 1 }}
                />
              ))}
            </Box>
          </SettingCard>

          {/* Data & Privacy */}
          <SettingCard
            title="Data & Privacy"
            icon={<SecurityIcon color="primary" />}
          >
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Your learning data is stored locally and never shared without your consent.
            </Typography>

            <Box mt={2}>
              <Button variant="outlined" sx={{ mr: 1 }}>
                Export Data
              </Button>
              <Button variant="outlined" color="error">
                Clear All Data
              </Button>
            </Box>
          </SettingCard>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box display="flex" justifyContent="flex-end" mt={3}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSave}
          sx={{ minWidth: 120 }}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;