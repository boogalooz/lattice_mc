from lattice_mc import init_lattice, species, lookup_table

class Simulation:

    def __init__( self ):
        self.lattice = None
        self.number_of_atoms = None
        self.number_of_jumps = None
        self.number_of_equilibration_jumps = 0
        self.atoms = None
        self.has_run = False

    def reset( self ):
        self.lattice.reset()
        for atom in self.atoms.atoms:
            atom.reset()
 
    def set_number_of_atoms( self, n ):
        self.number_of_atoms = n
        self.atoms = species.Species( self.lattice.populate_sites( self.number_of_atoms ) )

    def set_number_of_jumps( self, n ):
        self.number_of_jumps = n 

    def set_number_of_equilibration_jumps( self, n ):
        self.number_of_equilibration_jumps = n 

    def define_lattice_from_file( self, filename, cell_lengths ):
        self.lattice = init_lattice.lattice_from_sites_file( filename, cell_lengths = cell_lengths )

    def set_nn_energy( self,  nn_energy ):
        if nn_energy:
            self.lattice.set_nn_energy( nn_energy )

    def set_cn_energies( self, cn_energies ):
        if cn_energies:
            self.lattice.set_cn_energies( cn_energies )

    def set_site_energies( self, site_energies ):
        if site_energies:
            self.lattice.set_site_energies( site_energies )

    def run( self, for_time = None ):
        assert( self.lattice )
        assert( self.atoms )
        assert( self.number_of_jumps )
        if self.number_of_equilibration_jumps > 0:
            for step in range( self.number_of_equilibration_jumps ):
                self.lattice.jump()
            self.reset()
        if for_time:
           self.number_of_jumps = 0
           while self.lattice.time < for_time:
               self.lattice.jump()
               self.number_of_jumps += 1
        else: 
            for step in range( self.number_of_jumps ):
                self.lattice.jump()
        self.has_run = True

    def tracer_correlation( self ):
        assert( self.has_run )
        return self.atoms.sum_dr_squared() / float( self.number_of_jumps )

    def new_tracer_correlation( self ):
        assert( self.has_run )
        return self.atoms.tracer_correlation()

    def tracer_diffusion_coefficient( self ):
        assert( self.has_run )
        return self.atoms.sum_dr_squared() / ( 6.0 * float( self.number_of_atoms ) * self.lattice.time )

    def collective_correlation( self ):
        assert( self.has_run )
        return self.atoms.collective_dr_squared() / float( self.number_of_jumps )

    def new_collective_correlation( self ):
        assert( self.has_run )
        return self.atoms.collective_correlation()

    def collective_diffusion_coefficient( self ):
        assert( self.has_run )
        return self.atoms.collective_dr_squared() / ( 6.0 * self.lattice.time )

    def collective_diffusion_coefficient_per_atom( self ):
        assert( self.has_run )
        return self.collective_diffusion_coefficient() / float( self.number_of_atoms )

    def average_site_occupations( self ):
        return self.lattice.site_occupation_statistics()

    def setup_lookup_table( self, hamiltonian = 'nearest-neighbour' ):
        expected_hamiltonian_values = [ 'nearest-neighbour', 'coordination_number' ]
        assert( hamiltonian in expected_hamiltonian_values )
        self.lattice.jump_lookup_table = lookup_table.LookupTable( self.lattice, hamiltonian )