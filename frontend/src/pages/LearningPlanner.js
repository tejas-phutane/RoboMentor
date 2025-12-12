import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Fab,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Add as AddIcon,
  Timeline as TimelineIcon,
  CalendarToday as CalendarIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as UncheckedIcon,
  PlayArrow as PlayIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { format, addDays, startOfWeek } from 'date-fns';

const LearningPlanner = () => {
  const [goals, setGoals] = useState([
    {
      id: 1,
      title: 'Master Python Programming',
      description: 'Learn Python fundamentals for robotics applications',
      progress: 75,
      status: 'in_progress',
      domain: 'Programming',
      deadline: addDays(new Date(), 30),
    },
    {
      id: 2,
      title: 'ROS Framework',
      description: 'Understand Robot Operating System basics',
      progress: 45,
      status: 'in_progress',
      domain: 'Robotics',
      deadline: addDays(new Date(), 45),
    },
    {
      id: 3,
      title: 'Computer Vision',
      description: 'Learn image processing and object detection',
      progress: 20,
      status: 'in_progress',
      domain: 'AI/ML',
      deadline: addDays(new Date(), 60),
    },
  ]);

  const [learningPaths, setLearningPaths] = useState([
    {
      id: 1,
      title: 'Robotics Fundamentals',
      description: 'Complete foundation in robotics engineering',
      progress: 60,
      steps: [
        { id: 1, title: 'Introduction to Robotics', completed: true },
        { id: 2, title: 'Mechanical Systems', completed: true },
        { id: 3, title: 'Electronic Components', completed: false },
        { id: 4, title: 'Programming Basics', completed: false },
        { id: 5, title: 'Sensor Integration', completed: false },
      ],
    },
  ]);

  const [calendarEvents, setCalendarEvents] = useState([
    {
      id: '1',
      title: 'Python Study Session',
      start: new Date(),
      backgroundColor: '#1976d2',
    },
    {
      id: '2',
      title: 'ROS Tutorial',
      start: addDays(new Date(), 1),
      backgroundColor: '#388e3c',
    },
  ]);

  const [createGoalOpen, setCreateGoalOpen] = useState(false);
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    domain: 'Programming',
    deadline: '',
  });

  const domains = ['Programming', 'Robotics', 'AI/ML', 'Electronics', 'Mathematics'];

  const handleCreateGoal = () => {
    const goal = {
      id: goals.length + 1,
      ...newGoal,
      progress: 0,
      status: 'not_started',
      deadline: new Date(newGoal.deadline),
    };
    setGoals([...goals, goal]);
    setNewGoal({ title: '', description: '', domain: 'Programming', deadline: '' });
    setCreateGoalOpen(false);
  };

  const GoalCard = ({ goal }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box>
              <Typography variant="h6" gutterBottom>
                {goal.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {goal.description}
              </Typography>
              <Chip
                label={goal.domain}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
            <Chip
              label={`${goal.progress}%`}
              color={goal.progress === 100 ? 'success' : 'primary'}
              size="small"
            />
          </Box>

          <LinearProgress
            variant="determinate"
            value={goal.progress}
            sx={{ mb: 1, height: 8, borderRadius: 4 }}
          />

          <Typography variant="caption" color="textSecondary">
            Due: {format(goal.deadline, 'MMM dd, yyyy')}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  const LearningPathCard = ({ path }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {path.title}
          </Typography>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            {path.description}
          </Typography>

          <Box sx={{ mb: 2 }}>
            <LinearProgress
              variant="determinate"
              value={path.progress}
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
              {path.progress}% Complete
            </Typography>
          </Box>

          <Stepper orientation="vertical">
            {path.steps.map((step, index) => (
              <Step key={step.id} active={true}>
                <StepLabel
                  icon={
                    step.completed ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <UncheckedIcon color="disabled" />
                    )
                  }
                >
                  {step.title}
                </StepLabel>
                {index === path.steps.findIndex(s => !s.completed) && (
                  <StepContent>
                    <Button
                      size="small"
                      startIcon={<PlayIcon />}
                      variant="contained"
                      sx={{ mt: 1 }}
                    >
                      Start Learning
                    </Button>
                  </StepContent>
                )}
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Learning Planner
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateGoalOpen(true)}
        >
          New Goal
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Goals Section */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimelineIcon />
            Learning Goals
          </Typography>
          {goals.map(goal => (
            <GoalCard key={goal.id} goal={goal} />
          ))}
        </Grid>

        {/* Calendar Section */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarIcon />
            Schedule
          </Typography>
          <Card>
            <CardContent sx={{ p: 0 }}>
              <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                headerToolbar={{
                  left: 'prev,next today',
                  center: 'title',
                  right: 'dayGridMonth,timeGridWeek,timeGridDay'
                }}
                initialView="dayGridMonth"
                events={calendarEvents}
                height="400px"
                eventClick={(info) => {
                  alert(`Event: ${info.event.title}`);
                }}
                dateClick={(info) => {
                  alert(`Clicked on: ${info.dateStr}`);
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Learning Paths Section */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
            <TimelineIcon />
            Learning Paths
          </Typography>
          {learningPaths.map(path => (
            <LearningPathCard key={path.id} path={path} />
          ))}
        </Grid>
      </Grid>

      {/* Create Goal Dialog */}
      <Dialog open={createGoalOpen} onClose={() => setCreateGoalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Learning Goal</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Goal Title"
            fullWidth
            variant="outlined"
            value={newGoal.title}
            onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newGoal.description}
            onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            select
            margin="dense"
            label="Domain"
            fullWidth
            variant="outlined"
            value={newGoal.domain}
            onChange={(e) => setNewGoal({ ...newGoal, domain: e.target.value })}
            sx={{ mb: 2 }}
          >
            {domains.map((domain) => (
              <MenuItem key={domain} value={domain}>
                {domain}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            margin="dense"
            label="Deadline"
            type="date"
            fullWidth
            variant="outlined"
            InputLabelProps={{ shrink: true }}
            value={newGoal.deadline}
            onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateGoalOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateGoal}
            variant="contained"
            disabled={!newGoal.title || !newGoal.description || !newGoal.deadline}
          >
            Create Goal
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LearningPlanner;