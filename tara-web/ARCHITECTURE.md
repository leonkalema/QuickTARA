# TARA-Web Architecture Rulebook

## Project Structure

```
tara-web/
├── src/
│   ├── lib/
│   │   ├── stores/          # Global state management
│   │   ├── api/             # API layer and services
│   │   ├── types/           # TypeScript type definitions
│   │   ├── utils/           # Utility functions
│   │   └── constants/       # App constants and configurations
│   ├── features/            # Feature-based modules
│   │   ├── products/        # Product management
│   │   ├── assets/          # Asset management
│   │   ├── threats/         # Threat scenarios
│   │   └── damage/          # Damage scenarios
│   ├── components/          # Shared components
│   │   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   │   └── common/          # Common reusable components
│   └── routes/              # SvelteKit routes
```

## Design Principles

### 1. Feature-First Organization
- Each feature is self-contained in its own folder
- Features contain their own components, stores, and types
- No cross-feature dependencies (use global stores for shared state)

### 2. Global State Management
- Use Svelte stores for global state (selected product, user preferences)
- Persist critical state in localStorage
- Keep feature-specific state local to features

### 3. UI/UX Guidelines
- **No custom UI components** - Use Tailwind CSS classes directly
- Focus on clean, modern design with consistent spacing
- Prioritize usability and traceability
- Use semantic HTML elements
- Implement proper loading states and error handling

### 4. Component Rules
- Maximum 200 lines per component
- Single responsibility principle
- Props should be typed with TypeScript interfaces
- Use descriptive, action-oriented naming

### 5. API Layer
- Centralized API functions in `lib/api/`
- Consistent error handling across all API calls
- Type-safe API responses
- Loading and error states for all async operations

## Styling Standards

### Tailwind Usage
- Use utility classes directly in components
- Consistent color palette:
  - Primary: `blue-600` / `blue-700`
  - Success: `green-600` / `green-700`
  - Warning: `yellow-600` / `yellow-700`
  - Error: `red-600` / `red-700`
  - Gray scale: `gray-50` to `gray-900`

### Layout Patterns
- Use CSS Grid for complex layouts
- Flexbox for component-level layouts
- Consistent spacing: `space-y-4`, `space-x-4`, `p-4`, `m-4`
- Responsive design with mobile-first approach

### Interactive Elements
- Hover states for all clickable elements
- Focus states for accessibility
- Loading spinners for async operations
- Clear visual feedback for user actions

## Feature Development Workflow

### 1. Feature Structure
```
features/[feature-name]/
├── components/          # Feature-specific components
├── stores/             # Feature-specific stores
├── types/              # Feature-specific types
└── index.ts            # Feature exports
```

### 2. Development Steps
1. Define TypeScript types first
2. Create API functions
3. Build stores for state management
4. Develop components with proper error handling
5. Implement routes and navigation
6. Add comprehensive error states

### 3. Global State Integration
- Selected product must be available globally
- Use reactive statements to respond to global state changes
- Implement proper cleanup when switching contexts

## Code Quality Standards

### TypeScript
- Strict mode enabled
- No `any` types (use `unknown` if necessary)
- Proper interface definitions for all data structures
- Generic types where appropriate

### Error Handling
- Try-catch blocks for all async operations
- User-friendly error messages
- Fallback UI states for errors
- Proper loading states

### Performance
- Lazy load features when possible
- Optimize bundle size
- Use Svelte's reactivity efficiently
- Minimize unnecessary re-renders

## Navigation & UX Flow

### Global Product Selection
- Product selector in main navigation
- Persistent across all features
- Clear indication of current product
- Easy switching between products

### User Journey
1. **Product Selection** - Choose or create a product
2. **Asset Management** - Add/manage assets for selected product
3. **Threat Analysis** - Create threat scenarios for assets
4. **Damage Assessment** - Define damage scenarios
5. **Risk Analysis** - Analyze and mitigate risks

### Traceability
- Clear breadcrumbs showing current context
- Consistent navigation patterns
- Logical information hierarchy
- Easy access to related data

## Implementation Priorities

### Phase 1: Foundation
1. Global product store and selection
2. Clean navigation and layout
3. Product management (CRUD operations)

### Phase 2: Core Features
1. Asset management for selected product
2. Basic threat scenario creation
3. Damage scenario management

### Phase 3: Advanced Features
1. Risk analysis and reporting
2. Advanced filtering and search
3. Data export capabilities

## Testing Strategy

### Component Testing
- Test user interactions
- Test error states
- Test loading states
- Test accessibility

### Integration Testing
- Test feature workflows
- Test global state management
- Test API integration

### E2E Testing
- Test complete user journeys
- Test cross-feature interactions
- Test responsive design
