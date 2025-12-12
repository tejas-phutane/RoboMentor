import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Button,
  IconButton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  Timeline as TimelineIcon,
  EmojiEvents as TrophyIcon,
  Add as AddIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const Dashboard = () => {
  const [stats, setStats] = useState({
    skillsCount: 0,
    goalsCount: 0,
    pathsCount: 0,
    completedTasks: 0,
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [skillProgress, setSkillProgress] = useState([]);

  useEffect(() => {
    // Load dashboard data from backend
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Mock data for now - replace with actual API calls
      setStats({
        skillsCount: 8,
        goalsCount: 3,
        pathsCount: 2,
        completedTasks: 12,
      });

      setRecentActivity([
        { id: 1, type: 'goal', title: 'Completed Python Basics', time: '2 hours ago' },
        { id: 2, type: 'skill', title: 'Improved Data Structures knowledge', time: '1 day ago' },
        { id: 3, type: 'path', title: 'Started Robotics Learning Path', time: '2 days ago' },
      ]);

      setSkillProgress([
        { name: 'Python', level: 75, color: '#1976d2' },
        { name: 'Data Structures', level: 60, color: '#388e3c' },
        { name: 'Algorithms', level: 45, color: '#f57c00' },
        { name: 'Machine Learning', level: 30, color: '#d32f2f' },
      ]);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color}15, ${color}05)` }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" sx={{ color }}>
                {value}
              </Typography>
              {subtitle && (
                <Typography variant="body2" color="textSecondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
            <Avatar sx={{ bgcolor: color, width: 48, height: 48 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const SkillProgressCard = ({ skill }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h6">{skill.name}</Typography>
            <Chip
              label={`${skill.level}%`}
              size="small"
              sx={{ bgcolor: skill.color, color: 'white' }}
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={skill.level}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                bgcolor: skill.color,
                borderRadius: 4,
              },
            }}
          />
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Dashboard
      </Typography>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Skills Tracked"
            value={stats.skillsCount}
            icon={<SchoolIcon />}
            color="#1976d2"
            subtitle="Active learning areas"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Goals"
            value={stats.goalsCount}
            icon={<TrophyIcon />}
            color="#388e3c"
            subtitle="Current objectives"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Learning Paths"
            value={stats.pathsCount}
            icon={<TimelineIcon />}
            color="#f57c00"
            subtitle="Structured courses"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tasks Completed"
            value={stats.completedTasks}
            icon={<TrendingUpIcon />}
            color="#d32f2f"
            subtitle="This month"
          />
        </Grid>
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Skill Progress */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography variant="h5">Skill Progress</Typography>
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    size="small"
                  >
                    Add Skill
                  </Button>
                </Box>
                {skillProgress.map((skill, index) => (
                  <SkillProgressCard key={index} skill={skill} />
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  Recent Activity
                </Typography>
                <List>
                  {recentActivity.map((activity, index) => (
                    <React.Fragment key={activity.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            {activity.type === 'goal' && <TrophyIcon />}
                            {activity.type === 'skill' && <SchoolIcon />}
                            {activity.type === 'path' && <TimelineIcon />}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={activity.title}
                          secondary={activity.time}
                        />
                        <IconButton size="small">
                          <MoreIcon />
                        </IconButton>
                      </ListItem>
                      {index < recentActivity.length - 1 && <Divider variant="inset" />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;